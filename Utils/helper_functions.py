# karel.py
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math
from vision_msgs.msg import Detection2DArray
# import simpleaudio as sa

class UtilFunctions:
    def start():
        rclpy.init()

    def __init__(self, coco_file='coco.txt'):
        # rclpy.init()
        super().__init__('karel_util_node')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            Detection2DArray,
            '/detections',
            self.detection_callback,
            10
        )
        self.current_detections = []
        self.target_class_id = None

        # Load COCO classes
        self.coco_classes = self.load_coco_classes(coco_file)

    def move(self, velocity = 1.0):
        move_cmd = Twist()
        move_cmd.linear.x = velocity
        move_cmd.angular.z = 0.0 
        self.publisher.publish(move_cmd)
        rclpy.spin_once(self.node, timeout_sec=1.0)
        self.node.get_logger().info('Move forward...')
        time.sleep(1)
        self.stop()

    def turn(self, angular_velocity = 1.5): # positive is left
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = angular_velocity 
        self.publisher.publish(move_cmd)
        rclpy.spin_once(self.node, timeout_sec=1.0)
        self.node.get_logger().info('Turn left...')
        time.sleep(1)
        self.stop()

    def turn_to_heading(self, target_yaw, tolerance=0.01, angular_velocity=1.0):
        """
        Turns the robot to a specified heading angle.

        Args:
            target_yaw (float): The desired heading in radians.
            tolerance (float): The allowed error margin in radians.
            angular_velocity (float): The angular velocity for the turn.
        """
        rate = self.node.create_rate(10)  # 10 Hz
        self.node.get_logger().info(f"Turning to heading {math.degrees(target_yaw):.2f} degrees...")

        while True:
            # Compute the error
            error = target_yaw - self.current_yaw
            error = math.atan2(math.sin(error), math.cos(error))  # Normalize error to [-π, π]

            if abs(error) <= tolerance:
                self.node.get_logger().info("Reached target heading!")
                self.stop()
                break

            move_cmd = Twist()
            move_cmd.angular.z = angular_velocity if error > 0 else -angular_velocity
            self.publisher.publish(move_cmd)
            rclpy.spin_once(self.node, timeout_sec=0.1)
            rate.sleep()
    def turn_to_class(self, class_name, tolerance=0.01, angular_velocity=1.0, timeout=5.0):
        """
        Turns the robot to face the object with the specified class name.

        Args:
            class_name (str): The name of the object class to face.
            tolerance (float): Allowed angular error margin.
            angular_velocity (float): Angular velocity for turning.
            timeout (float): Time limit to find and face the object.
        """
        if class_name not in self.coco_classes:
            self.get_logger().error(f"Class '{class_name}' not found in COCO dataset.")
            return

        class_id = self.coco_classes[class_name]
        self.get_logger().info(f"Turning to face object with class_name='{class_name}', class_id={class_id}...")

        start_time = time.time()
        rate = self.create_rate(10)  # 10 Hz

        while rclpy.ok():
            # Timeout check
            if time.time() - start_time > timeout:
                self.get_logger().warn("Timeout reached while searching for the object.")
                self.stop()
                return

            # Look for the target class in the current detections
            target_detection = None
            for detection in self.current_detections:
                if detection.results[0].id == class_id:
                    target_detection = detection
                    break

            if target_detection:
                # Calculate the error in the object's position relative to the center of the image
                image_width = 1400  # Assume an image width for calculations
                bbox_center_x = target_detection.bbox.center.position.x
                error = (bbox_center_x - (image_width / 2)) / (image_width / 2)  # Normalize to [-1, 1]

                if abs(error) <= tolerance:
                    self.get_logger().info("Object centered!")
                    self.stop()
                    return

                # Adjust angular velocity to reduce the error
                move_cmd = Twist()
                move_cmd.angular.z = angular_velocity * -error
                self.publisher.publish(move_cmd)

            else:
                self.get_logger().info("Target class not detected. Rotating to search...")
                # Perform a simple search behavior if the object is not detected
                move_cmd = Twist()
                move_cmd.angular.z = angular_velocity
                self.publisher.publish(move_cmd)

            rclpy.spin_once(self, timeout_sec=0.1)
            rate.sleep()

   

#     def bark(self):
#         self.node.get_logger().info('Bark...')
#         pygame.mixer.init()
#         bark_sound = pygame.mixer.Sound('/home/pi/pupper_llm/sounds/dog_bark.wav')
#         bark_sound.play()
        
# #        time.sleep(0.5)
#         self.stop()


    def stop(self):
        self.node.get_logger().info('Stopping...')
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.linear.y = 0.0
        move_cmd.linear.z = 0.0
        move_cmd.angular.x = 0.0
        move_cmd.angular.y = 0.0
        move_cmd.angular.z = 0.0
        self.publisher.publish(move_cmd)
        rclpy.spin_once(self.node, timeout_sec=1.0)
    
    def __del__(self):
        self.node.get_logger().info('Tearing down...')
        self.node.destroy_node()
        rclpy.shutdown()