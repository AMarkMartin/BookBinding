import unittest
import json
from app import app

class BindingAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bookbinding Template Generator', response.data)

    def test_api_generate(self):
        payload = {
            'book_w': 150,
            'book_h': 230,
            'book_t': 20,
            'num_hubs': 4
        }
        response = self.app.post('/api/generate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('<svg', data['svg'])
        self.assertIn('measurements', data)
        self.assertEqual(len(data['measurements']['hubs']), 4)

if __name__ == '__main__':
    unittest.main()
