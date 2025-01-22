import os
import json
from pydantic import BaseModel, Field
from AWS.CloudWatchLogs import get_logger
import AWS.DynamoDB as DynamoDB
from LLM.CreateLLM import create_llm
from LLM.LLMExtract import llm_extract
from Models import Agent, Job

# Set up the logger
logger = get_logger(log_level=os.environ["LOG_LEVEL"])

# Create agent event
class CreateAgentEvent(BaseModel):
    org_id: str
    job_id: str
    agent_template_id: str
    business_name: str
    business_description: str
    additional_link_info: str

class CreateAgent(BaseModel):
    """Creates an agent with the name, description, and prompt"""
    agent_name: str = Field(description="The name of the agent, something catchy that will be easily rememberable and is unique to the business")
    agent_description: str = Field(description="Short description of the agent and it's purpose")
    prompt: str = Field(description="Prompt that instructs the agent to perform it's role")


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event: dict, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    # Parse the event
    try:
        event = CreateAgentEvent(**event)
    except Exception as e:
        logger.error(str(e))
        return {
            'error': str(e)
        }

    # Check if the job exists
    if (not Job.job_exists(event.job_id)):
        logger.error(f"Job {event.job_id} not found")
        return {
            'error': f"Job {event.job_id} not found"
        }

    try:
        # Get the agent template prompt from agent_template_id
        agent_template = DynamoDB.get_item("agent_templates", "agent_template_id", event.agent_template_id)
        if (agent_template is None):
            raise Exception("Agent template not found")
        agent_template_prompt = agent_template["prompt"]

        # Insert business_name and additional_info into prompt
        agent_template_prompt = agent_template_prompt.format(
            business_name=event.business_name,
            additional_information=f"{event.business_description} {event.additional_link_info}"
        )
        
        # Extract the agent details
        llm = create_llm()
        extract_agent = llm_extract(CreateAgent, agent_template_prompt, llm)
        extract_agent = CreateAgent(**extract_agent)
        logger.info(f"Extracted agent: {extract_agent}")

        # Create the agent
        agent = Agent.create_agent(
            agent_name=extract_agent.agent_name,
            agent_description=extract_agent.agent_description,
            prompt=extract_agent.prompt,
            org_id=event.org_id,
            is_public=False,
            agent_speaks_first=True
        )

        # Get the Job
        job = Job.get_job(event.job_id)
        
        # Set job's data agent_template_id as true
        job.data[event.agent_template_id]["completed"] = True
        job.data[event.agent_template_id]["agent_id"] = agent.agent_id

        # Set complete if all other agent_templates_id are true
        is_complete = True
        for agent_template_id in job.data.keys():
            is_complete = is_complete and job.data[agent_template_id]["completed"]
        if is_complete:
            job.status = Job.JobStatus.completed

        # Save the job status
        Job.save_job(job)

        # Return the model
        return agent.model_dump()

    # Return any errors and set the job status to error  
    except Exception as e:
        logger.error(str(e))
        job = Job.get_job(event.job_id)
        job.status = "error"
        job.message = str(e)
        Job.save_job(job)
