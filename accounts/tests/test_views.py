from .test_setup import TestCaseSetUp
import django

class TestViews(TestCaseSetUp):
    """Tests on views functionalities"""

    def test_user_cannot_register_without_data(self):
        res=self.client.post(self.register_url)

        self.assertEqual(res.status_code, 400)

    def test_user_can_register_correctly_with_data(self):
        res=self.client.post(self.register_url, data=self.user_data, format="json") 
        
        import pdb
        pdb.set_trace()
        self.assertEqual(res.data["email"], self.user_data["email"])
        self.assertEqual(res.data["first_name"], self.user_data["first_name"])
        self.assertEqual(res.data["last_name"], self.user_data["last_name"])
        self.assertEqual(res.data["dob"], self.user_data["dob"])
        self.assertEqual(res.data["password"], self.user_data["password"])
        self.assertEqual(res.data["confirm_password"], self.user_data["confirm_password"])

        self.assertEqual(res.status_code, 201)