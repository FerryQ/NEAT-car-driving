import pygame
import neat
from colours import Color as colours

pygame.font.init()

class NodeType:
    INPUT = 0
    HIDDEN = 1
    OUTPUT = 2

class NN:
    INPUT_NEURONS = 5
    OUTPUT_NEURONS = 4

    def __init__(self, config: neat.Config, genome: neat.DefaultGenome, pos: tuple):
        self.genome = genome
        self.pos = (int(pos[0] + Node.RADIUS), int(pos[1]))
        self.nodes = []
        self.connections = []

        input_labels = ["0°", "90°", "-90°", "30°", "-30°","speed","angle"]
        output_labels = ["Left", "Right", "Accelerate", "Brake","Release"]
        node_id_list = []

        # Gather all node IDs
        hidden_node_ids = list(genome.nodes.keys())

        # --- Input Nodes ---
        input_spacing = Node.RADIUS * 2 + Node.SPACING
        input_offset = (self.INPUT_NEURONS - 1) * input_spacing
        for i, input_id in enumerate(config.genome_config.input_keys):
            y = pos[1] + int(-input_offset / 2 + i * input_spacing)
            node = Node(
                input_id, pos[0], y,
                NodeType.INPUT,
                [colours.GREEN_PALE, colours.GREEN, colours.DARK_GREEN_PALE, colours.DARK_GREEN],
                input_labels[i], i
            )
            self.nodes.append(node)
            node_id_list.append(input_id)

        # --- Output Nodes ---
        output_spacing = Node.RADIUS * 2 + Node.SPACING
        output_offset = (self.OUTPUT_NEURONS - 1) * output_spacing
        output_x = pos[0] + 2 * (Node.LAYER_SPACING + 2 * Node.RADIUS)

        for i, output_id in enumerate(config.genome_config.output_keys):
            y = pos[1] + int(-output_offset / 2 + i * output_spacing)
            node = Node(
                output_id, output_x, y,
                NodeType.OUTPUT,
                [colours.RED_PALE, colours.RED, colours.DARK_RED_PALE, colours.DARK_RED],
                output_labels[i], i
            )
            self.nodes.append(node)
            hidden_node_ids.remove(output_id)
            node_id_list.append(output_id)

        # --- Hidden Nodes ---
        hidden_spacing = Node.RADIUS * 2 + Node.SPACING
        hidden_offset = (len(hidden_node_ids) - 1) * hidden_spacing
        hidden_x = self.pos[0] + (Node.LAYER_SPACING + 2 * Node.RADIUS)

        for i, hidden_id in enumerate(hidden_node_ids):
            y = self.pos[1] + int(-hidden_offset / 2 + i * hidden_spacing)
            node = Node(
                hidden_id, hidden_x, y,
                NodeType.HIDDEN,
                [colours.BLUE_PALE, colours.DARK_BLUE, colours.BLUE_PALE, colours.DARK_BLUE]
            )
            self.nodes.append(node)
            node_id_list.append(hidden_id)

        # --- Connections ---
        for connection in genome.connections.values():
            if not connection.enabled:
                continue

            input_id, output_id = connection.key
            input_node = self.nodes[node_id_list.index(input_id)]
            output_node = self.nodes[node_id_list.index(output_id)]

            # Only add valid connections between types
            if (input_node.type == NodeType.INPUT and output_node.type in {NodeType.HIDDEN, NodeType.OUTPUT}) or \
               (input_node.type == NodeType.HIDDEN and output_node.type == NodeType.OUTPUT):
                self.connections.append(Connection(input_node, output_node, connection.weight))

    def draw(self, screen: pygame.Surface):
        for c in self.connections:
            c.draw(screen)
        for node in self.nodes:
            node.draw(screen)

    

class Node:
    RADIUS = 20
    SPACING = 5
    LAYER_SPACING = 100
    CONNECTION_WIDTH = 2
    FONT = pygame.font.SysFont('Comic Sans MS', 15)

    def __init__(self, id: int, x: int, y: int, type: NodeType, colours: list[colours], label: str = "", index: int = 0):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.colours = colours
        self.label = label
        self.index = index
        self.inputs = [0, 0, 0, 0, 0, 0, 0]
        self.output = None

    def draw(self, screen: pygame.Surface):

        colour_scheme = self.get_colour()

        """
        ILUSTRATION PURPOSES
        if self.type ==  NodeType.INPUT:
            pygame.draw.circle(
            screen,(255,255,255), (self.x, self.y), Node.RADIUS)
            pygame.draw.circle(
            screen,(0,255,0), (self.x, self.y), Node.RADIUS - 2)
        
        if self.type ==  NodeType.OUTPUT:
            pygame.draw.circle(
            screen, (255,255,255), (self.x, self.y), Node.RADIUS)
            pygame.draw.circle(
            screen, (255,0,0), (self.x, self.y), Node.RADIUS - 2)

        """
        pygame.draw.circle(
            screen, colour_scheme[0], (self.x, self.y), Node.RADIUS)
        pygame.draw.circle(
            screen, colour_scheme[1], (self.x, self.y), Node.RADIUS - 2)
        

        if self.type != NodeType.HIDDEN:
            text = Node.FONT.render(self.label, 1, colours.WHITE)
            screen.blit(text, (self.x + (self.type-1) * ((text.get_width()
                            if not self.type else 0) + Node.RADIUS + 5), self.y - text.get_height()/2))
        

    def get_colour(self):
        if self.type == NodeType.INPUT:
            v = self.inputs[self.index]
            ratio = 1 - (min(v / 100, 1))
        elif self.type == NodeType.OUTPUT:
            ratio = 1 if self.index == self.output else 0
        else:
            ratio = 0

        colour = [[0, 0, 0], [0, 0, 0]]
        for i in range(3):
            colour[0][i] = int(ratio * (self.colours[1][i] - self.colours[3][i]) + self.colours[3][i]) % 256
            colour[1][i] = int(ratio * (self.colours[0][i] -
                            self.colours[2][i]) + self.colours[2][i]) % 256
        return colour

class Connection:
    def __init__(self, input, output, wt):
        self.input = input
        self.output = output
        self.wt = wt

    def draw(self, screen):
        colour = colours.GREEN if self.wt >= 0 else colours.RED
        width = int(abs(self.wt * Node.CONNECTION_WIDTH))
        pygame.draw.line(screen, colour, (self.input.x + Node.RADIUS,
                         self.input.y), (self.output.x - Node.RADIUS, self.output.y), width)


        