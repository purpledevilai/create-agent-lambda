from pydantic import Field, BaseModel
from LLM.AgentChat import AgentTool

# This name must match what you are referencing in the prompt
class pass_event(BaseModel):
  type: str = Field(description="The draft or version of the prompt")
  data: str = Field(description="The draft or version of the prompt")

# Function params must match base model params
def pass_event_func(type: str, data: str, context: dict) -> str:
  if "events" not in context:
    context["events"] = []
  context["events"].append({
    "type": type,
    "data": data
  })
  return f"Event of type {type} added!"

# This is the tool that will be used in the agent chat
pass_event_tool = AgentTool(params=pass_event, function=pass_event_func, pass_context=True)