import pytest
import pygame
from pygame.math import Vector2 as vec2
import math

from car import NormalCar, DriftCar, AbstractCar
from sensors import Sensor
from game import Game_info

# @generated "mostly" gemini-pro: make unit tests
pygame.init()


@pytest.fixture
def mock_surface():
    surface = pygame.Surface((50, 20))
    surface.fill((255, 0, 0))
    return surface


@pytest.fixture
def mock_game_map():
    surface = pygame.Surface((1400, 1080))
    surface.fill((0, 0, 0))
    pygame.draw.rect(surface, (255, 255, 255), (0, 0, 1400, 10), 0)  # Top
    pygame.draw.rect(surface, (255, 255, 255), (0, 1070, 1400, 10), 0)  # Bottom
    pygame.draw.rect(surface, (255, 255, 255), (0, 0, 10, 1080), 0)  # Left
    pygame.draw.rect(surface, (255, 255, 255), (1390, 0, 10, 1080), 0)  # Right
    return surface


# --- Tests for Game_info ---
class TestGameInfo:
    def test_game_info_initialization(self):
        game_info = Game_info()
        assert not game_info.started
        assert not game_info.exited
        assert not game_info.levels_menu
        assert not game_info.drift_car
        assert not game_info.normal_car

    def test_game_info_reset(self):
        game_info = Game_info()
        # Change some values
        game_info.started = True
        game_info.levels_menu = True
        game_info.drift_car = True
        game_info.level_one = True

        game_info.reset()

        assert not game_info.started
        assert not game_info.exited
        assert not game_info.levels_menu
        assert not game_info.drift_car
        assert not game_info.normal_car
        assert not game_info.level_one
        assert not game_info.new_generation


# --- Tests for Sensor ---
class TestSensor:
    def test_sensor_initialization(self, mock_surface):
        sensor = Sensor(mock_surface, start=(0, 0), end=(10, 10))
        assert sensor.start == (0, 0)
        assert sensor.end == (10, 10)
        assert sensor.img_width == mock_surface.get_width()
        assert sensor.img_height == mock_surface.get_height()
        assert sensor.length == 2000
        assert sensor.collision_vec == (0, 0)

    def test_sensor_set_start_end(self, mock_surface):
        sensor = Sensor(mock_surface)
        sensor.set_start((5, 5))
        sensor.set_end((15, 15))
        assert sensor.start == (5, 5)
        assert sensor.end == (15, 15)

    def test_sensor_calculate_line_forward(self, mock_surface):
        sensor = Sensor(mock_surface)
        car_x, car_y = 100, 100
        angle = 0
        sensor.calculate_line(mock_surface, car_x, car_y, angle)

        expected_start_x = car_x + mock_surface.get_width() / 2
        expected_start_y = car_y + mock_surface.get_height() / 2
        assert sensor.start == (expected_start_x, expected_start_y)

        expected_end_x = expected_start_x + sensor.length * math.cos(
            math.radians(angle)
        )
        expected_end_y = expected_start_y - sensor.length * math.sin(
            math.radians(angle)
        )
        assert math.isclose(sensor.end[0], expected_end_x)
        assert math.isclose(sensor.end[1], expected_end_y)

    def test_sensor_distance_no_collision(self, mock_surface):
        sensor = Sensor(mock_surface, start=(0, 0))
        sensor.collision_vec = (0, 0)  #
        assert sensor.distance() == 0

    def test_sensor_distance_with_collision(self, mock_surface):
        sensor = Sensor(mock_surface, start=(0, 0))
        sensor.collision_vec = (30, 40)
        assert math.isclose(sensor.distance(), 50)

    def test_sensor_line_collide_no_collision(self, mock_surface, mock_game_map):
        sensor = Sensor(mock_surface)
        # Place sensor pointing into empty space
        sensor.start = (200, 200)
        sensor.end = (300, 200)  # Horizontal line in empty space
        assert sensor.line_collide(mock_game_map) is None
        assert sensor.collision_vec == (0, 0)  # Should not update if no collision

    def test_sensor_line_collide_with_collision(self, mock_surface, mock_game_map):
        sensor = Sensor(mock_surface)
        # Point sensor towards a white border
        sensor.start = (50, 50)  # Inside the track
        sensor.end = (50, 5)  # Pointing upwards towards the top border

        collision_point = sensor.line_collide(mock_game_map)
        assert collision_point is not None
        assert collision_point[1] < 10  # Should collide with top border (y < 10)
        assert sensor.collision_vec == collision_point


# --- Tests for AbstractCar (and its derivatives NormalCar, DriftCar) ---
@pytest.fixture
def normal_car(mock_surface, mock_game_map):
    return NormalCar(
        max_vel=5,
        rotation_vel=4,
        start_pos=(100, 100),
        car_image=mock_surface,
        game_map=mock_game_map,
        best_car=mock_surface,
    )


@pytest.fixture
def drift_car(mock_surface, mock_game_map):
    return DriftCar(
        max_vel=6,
        rotation_vel=4,
        start_pos=(100, 100),
        car_image=mock_surface,
        game_map=mock_game_map,
        best_car=mock_surface,
    )


class TestAbstractCar:
    def test_car_initialization(self, normal_car, mock_surface):
        assert normal_car.vel == 0
        assert normal_car.angle == 0
        assert normal_car.x == 100 and normal_car.y == 100
        assert normal_car.alive
        assert len(normal_car.sensors) == 5
        assert normal_car.img == mock_surface

    def test_car_rotate_left(self, normal_car):
        initial_angle = normal_car.angle
        rotation_amount = normal_car.rotation_vel
        normal_car.rotate(left=True)
        assert normal_car.angle == initial_angle + rotation_amount

    def test_car_rotate_right(self, normal_car):
        initial_angle = normal_car.angle
        rotation_amount = normal_car.rotation_vel
        normal_car.rotate(right=True)
        assert normal_car.angle == initial_angle - rotation_amount

    def test_car_start_accel(self, normal_car):
        normal_car.start_accel()
        assert normal_car.accelerate
        assert not normal_car.brake

    def test_car_start_brake(self, normal_car):
        normal_car.start_brake()
        assert normal_car.brake
        assert not normal_car.accelerate

    def test_car_release_pedals(self, normal_car):
        normal_car.start_accel()  # Set a state
        normal_car.release_pedals()
        assert not normal_car.accelerate
        assert not normal_car.brake

    def test_car_is_alive(self, normal_car):
        assert normal_car.is_alive()
        normal_car.alive = False
        assert not normal_car.is_alive()

    def test_car_reset(self, normal_car):
        normal_car.x, normal_car.y = (200, 200)
        normal_car.angle = 90
        normal_car.vel = 5
        normal_car.accelerate = True
        normal_car.alive = True  # Ensure it's alive before reset to check other props

        normal_car.reset()

        assert normal_car.x == normal_car.start_pos[0]
        assert normal_car.y == normal_car.start_pos[1]
        assert normal_car.angle == 0
        assert normal_car.vel == 0
        assert not normal_car.accelerate
        assert not normal_car.brake
        # `alive` status is not reset by car.reset(), it's usually set by collision logic
        assert normal_car.alive


class TestNormalCarMovement:
    def test_normal_car_accelerate(self, normal_car):
        normal_car.start_accel()
        initial_pos = normal_car.position.copy()
        initial_vel = normal_car.vel

        # Simulate a few updates
        for _ in range(5):
            normal_car.move()  # move() updates velocity and position

        assert normal_car.vel > initial_vel
        assert normal_car.vel <= normal_car.max_vel
        # Position should change based on angle 0 (moves along x-axis)
        assert normal_car.position.x > initial_pos.x
        assert math.isclose(
            normal_car.position.y, initial_pos.y
        )  # No vertical movement if angle is 0

    def test_normal_car_brake(self, normal_car):
        # First, give it some speed
        normal_car.start_accel()
        for _ in range(10):
            normal_car.move()

        assert normal_car.vel > 0

        normal_car.start_brake()
        initial_vel_before_braking = normal_car.vel
        for _ in range(5):
            normal_car.move()

        assert normal_car.vel < initial_vel_before_braking

    def test_normal_car_no_pedal_friction(self, normal_car):
        normal_car.start_accel()
        for _ in range(10):
            normal_car.move()
        assert normal_car.vel > 0

        normal_car.release_pedals()
        initial_vel_after_accel = normal_car.vel
        for _ in range(10):  # Simulate friction acting
            normal_car.move()

        assert normal_car.vel < initial_vel_after_accel
        assert normal_car.vel >= 0  # Should not go negative from friction alone


class TestDriftCarMovement:
    def test_drift_car_accelerate(self, drift_car):
        drift_car.start_accel()
        initial_pos = drift_car.position.copy()
        initial_vel_mag = drift_car.velocity.length()

        for _ in range(5):
            drift_car.move()

        assert drift_car.velocity.length() > initial_vel_mag
        assert drift_car.velocity.length() <= drift_car.max_speed
        assert drift_car.position.x > initial_pos.x
        assert math.isclose(drift_car.position.y, initial_pos.y)

    def test_drift_car_friction_and_drift(self, drift_car):
        # Give it some speed and an angle
        drift_car.angle = 45
        drift_car.start_accel()
        for _ in range(10):
            drift_car.move()

        assert drift_car.velocity.length() > 0

        drift_car.release_pedals()
        initial_velocity_vector = drift_car.velocity.copy()
        initial_position = drift_car.position.copy()

        for _ in range(10):
            drift_car.move()

        # Velocity magnitude should decrease due to friction
        assert drift_car.velocity.length() < initial_velocity_vector.length()

        # Check if car has moved (drifted)
        # With an angle, both x and y should change
        assert not math.isclose(
            drift_car.position.x, initial_position.x
        ) or not math.isclose(drift_car.position.y, initial_position.y)

    def test_drift_car_get_reward(self, drift_car):
        # Basic reward check
        drift_car.velocity = vec2(3, 0)  # Moving forward
        drift_car.forward = vec2(1, 0)  # Facing forward
        drift_car.time = 10
        drift_car.distance = 100
        reward = drift_car.get_reward()
        # Expected: (3*5) - (10/10) + 100 = 15 - 1 + 100 = 114
        assert math.isclose(reward, (3 * 5) - (10 / 10) + 100)

        # Reward when moving backward (penalty)
        drift_car.velocity = vec2(-2, 0)  # Moving backward
        reward_backward = drift_car.get_reward()
        assert reward_backward < 0  # Should be a large negative number
