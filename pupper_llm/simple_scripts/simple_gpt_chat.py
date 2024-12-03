import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from openai import OpenAI

client = OpenAI(api_key='')

class GPT4ConversationNode(Node):
    def __init__(self):
        super().__init__('gpt4_conversation_node')

        # Create a subscriber to listen to user queries
        self.subscription = self.create_subscription(
            String,
            'user_query_topic',  # Replace with your topic name for queries
            self.query_callback,
            10
        )

        # Create a publisher to send back responses
        self.publisher_ = self.create_publisher(
            String,
            'gpt4_response_topic',  # Replace with your topic name for responses
            10
        )

        self.get_logger().info('GPT-4 conversation node started and waiting for queries...')

    def query_callback(self, msg):
        # Extract the user query from the message
        query = msg.data

        # Call GPT-4 API to get the response
        response = self.get_gpt4_response(query)

        # Create a new String message for the response
        response_msg = String()
        response_msg.data = response

        # Publish the response
        self.publisher_.publish(response_msg)

        # DEBUG LOGGERS
        self.get_logger().info(f"Received user query: {query}") 
        self.get_logger().info(f"Published GPT-4 response: {response}")

    def get_gpt4_response(self, query):
        try:
            # Making the API call to GPT-4 using OpenAI's Python client
            prompt = "You are a helpful assistant. Please provide a concise response to the following query:"
            response = client.chat.completions.create(
                model="gpt-4",  # Model identifier, assuming GPT-4 is used
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=150  # Adjust token limit based on your requirement
            )

            # Extract the assistant's reply from the response
            gpt4_response = response.choices[0].message.content
            return gpt4_response

        except Exception as e:
            self.get_logger().error(f"Error calling GPT-4 API: {str(e)}")
            return "Sorry, I couldn't process your request due to an error."

def main(args=None):
    rclpy.init(args=args)

    # Create the node and spin it
    gpt4_conversation_node = GPT4ConversationNode()
    rclpy.spin(gpt4_conversation_node)

    # Clean up and shutdown
    gpt4_conversation_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()