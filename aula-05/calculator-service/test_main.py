import unittest
from main import calculate_logic

class TestCalculator(unittest.TestCase):
    def test_add(self):
        data = {"operation": "add", "a": 10, "b": 5}
        res, status = calculate_logic(data)
        self.assertEqual(status, 200)
        self.assertEqual(res["result"], 15)

    def test_subtract(self):
        data = {"operation": "subtract", "a": 10, "b": 5}
        res, status = calculate_logic(data)
        self.assertEqual(status, 200)
        self.assertEqual(res["result"], 5)

    def test_multiply(self):
        data = {"operation": "multiply", "a": 10, "b": 5}
        res, status = calculate_logic(data)
        self.assertEqual(status, 200)
        self.assertEqual(res["result"], 50)

    def test_divide(self):
        data = {"operation": "divide", "a": 10, "b": 5}
        res, status = calculate_logic(data)
        self.assertEqual(status, 200)
        self.assertEqual(res["result"], 2)

    def test_divide_by_zero(self):
        data = {"operation": "divide", "a": 10, "b": 0}
        res, status = calculate_logic(data)
        self.assertEqual(status, 400)
        self.assertIn("error", res)

    def test_invalid_operation(self):
        data = {"operation": "invalid", "a": 10, "b": 5}
        res, status = calculate_logic(data)
        self.assertEqual(status, 400)
        self.assertIn("error", res)

if __name__ == '__main__':
    unittest.main()
