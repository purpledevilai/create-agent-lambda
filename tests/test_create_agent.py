import json
import unittest
import sys
sys.path.append("../")
from tests.config import org_id, job_id, additional_link_info
from src.lambda_function import lambda_handler


class TestCreateAgent(unittest.TestCase):

    def test_create_agent(self):

        event = {
            "org_id": org_id,
            "job_id": job_id,
            "agent_template_id": "customer-support",
            "business_name": "Cleaningly",
            "business_description": "Were a business that cleans your residential and clinical spaces",
            "additional_link_info": additional_link_info
        }

        # Call the lambda handler
        result = lambda_handler(event, None)
        print(result)

        # Check the response
        self.assertIsNotNone(result)

    

    