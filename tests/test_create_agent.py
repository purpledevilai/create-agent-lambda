import unittest
import sys
sys.path.append("../")
from tests.config import org_id, user_id, additional_link_info
from src.lambda_function import lambda_handler
from src.Models import Job, Agent


class TestCreateAgent(unittest.TestCase):

    def test_create_agent(self):

        # Set up
        job = Job.create_job(
            owner_id=user_id,
            data={
                "customer-support": False
            }
        )

        event = {
            "org_id": org_id,
            "job_id": job.job_id,
            "agent_template_id": "customer-support",
            "business_name": "Cleaningly",
            "business_description": "Were a business that cleans your residential and clinical spaces",
            "additional_link_info": additional_link_info
        }

        # Call the lambda handler
        result = lambda_handler(event, None)
        print(result)

        # Assert response has agent_id
        self.assertTrue("agent_id" in result)

        # Clean up
        Job.delete_job(job.job_id)
        Agent.delete_agent(result["agent_id"])

    

    