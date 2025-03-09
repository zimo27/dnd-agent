import random
import openai
from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = ""
client = OpenAI()
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Ensure your API key is set in the environment
    

def generate_connected_map(width, height, fill_ratio=0.5):
    """
    Generate a randomly connected D&D map.
    
    Args:
        width (int): Number of columns.
        height (int): Number of rows.
        fill_ratio (float): Fraction of the grid to be standable (1's).
    
    Returns:
        list of list of int: The generated map, with 0 for wall and 1 for standable area.
    """
    total_cells = width * height
    target_floor_count = int(total_cells * fill_ratio)
    
    # Create grid filled with walls (0)
    grid = [[0 for _ in range(width)] for _ in range(height)]
    floor_count = 0
    
    # Pick a random starting cell and mark it as standable
    start_x = random.randrange(width)
    start_y = random.randrange(height)
    grid[start_y][start_x] = 1
    floor_count += 1

    # Frontier: all wall cells that are adjacent to the standable region.
    frontier = set()

    def add_frontier(x, y):
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0:
                frontier.add((nx, ny))
    
    add_frontier(start_x, start_y)
    
    # Grow the standable region until we hit the target fill ratio
    while frontier and floor_count < target_floor_count:
        # Choose a random frontier cell
        cell = random.choice(list(frontier))
        x, y = cell
        grid[y][x] = 1
        floor_count += 1
        frontier.remove(cell)
        add_frontier(x, y)
    
    return grid

def gpt_polish(grid, story, enemy_list):
    enemy_list_str = " ".join(f"{enemy}" for enemy in enemy_list)
    prompt = (
        f"Story: {story}\n"
        f"You are given the following map where 1 stands for valid area and 0 stands for invalid area: \n{grid}\n"
        f"As an experienced dungeon master, you will decide the location of the player and all other enemies, including {enemy_list_str}. "
        "Besides, you will think of what other related objects could be, which are highly aligned with the background story. "
        "The objects, different from the plain ground, decides the height of the map. Player gains advantage if they are on a higher ground. "
        "Finally, you will make sure this is an interesting yet challenging battle. "
        "For each enemy in the enemy_list, make sure you return a pair of coordinates for their location. "
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are anexperienced dungeon master."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    print(response.choices[0].message.content)

def print_map(grid):
    for row in grid:
        print(" ".join(map(str, row)))

# Example usage:
if __name__ == "__main__":
    width, height = 10, 10  # you can set x and y dimensions here
    dungeon_map = generate_connected_map(width, height, fill_ratio=0.5)
    
    story = """King's Quarters

    Any character who listens at the door hears two voices in a heated discussion— a loud, growling voice demanding payment for something, and a silky smooth reply. This chamber has been set up as a crude living space, with thick furs thrown on the floor to serve as carpets, old trophies hanging on the walls, a large bed to the north, and a brazier of coals burning brightly. A round table with several chairs stands to the south near the door. Near the table, on the floor, is an unconscious dwarf who looks badly beaten.

    King Grol is a fierce old bugbear with 45 hit points. He rules the Cragmaws through pure intimidation. Age has stooped his shoulders and hunched his back, but he remains surprisingly agile and strong. He is demanding and vindictive, and no Cragmaw dares to cross him.

    Grol is attended by Snarl, a wolf with 18 hit points, and a doppelganger disguised as a female drow. The doppelganger, Vyerith, is a messenger from the Black Spider, come to collect Gundren Rockseeker and the map of Wave Echo Cave from King Grol. Grol wants to sell the map instead of surrendering it, and he and the drow are negotiating a price. Vyerith first wants to question Gundren to find out if anyone else knows the location of the mine. Then the doppelganger intends to kill the dwarf and destroy the map.

    If the villains have been warned that an attack is imminent, Vyerith hides behind the door to the northeast, leaving it open a crack and hoping to attack an intruder from the rear. Grol holds Gundren hostage, ready to kill the dwarf if the characters don’t back off.

    Awarding Experience Points:
    Divide 950 XP equally among the characters if the party defeats King Grol, the wolf, and the doppelganger. Award an additional 200 XP to the party if the characters rescue Gundren Rockseeker and escort him safely back to Phandalin.
    """
    
    dungeon_map_str = "\n".join(" ".join(map(str, row)) for row in dungeon_map)
    gpt_polish(dungeon_map_str, story, ['King Grol', 'Snarl', 'Vyerith'])

    

    
