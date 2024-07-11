import random
from itertools import combinations, permutations
import io
from PIL import Image
import json
from tqdm import tqdm
import os
import multiprocessing as mp
import base64

class Card:
    def __init__(self, color, shape, number, shading):
        self.color = color
        self.shape = shape
        self.number = number
        self.shading = shading
        self.image = f"card_images/{color}{shape}{shading}{number}.png"

    def to_dict(self):
        return {
            "color": self.color,
            "shape": self.shape,
            "number": self.number,
            "shading": self.shading,
            "image": self.image
        }

    def to_string(self):
        number_map = {"1": "One", "2": "Two", "3": "Three"}
        return f"<number>{number_map[self.number]}</number> <color>{self.color.capitalize()}</color> <shading>{self.shading.capitalize()}</shading> <shape>{self.shape.capitalize()}</shape>"

def generate_cards():
    colors = ["red", "green", "purple"]
    shapes = ["diamond", "oval", "squiggle"]
    numbers = ["1", "2", "3"]
    shadings = ["empty", "filled", "shaded"]

    all_cards = [Card(c, s, n, sh) for c in colors for s in shapes for n in numbers for sh in shadings]
    return random.sample(all_cards, 12)

def is_set(card1, card2, card3):
    return all(len(set(getattr(card, attr) for card in [card1, card2, card3])) != 2 
               for attr in ["color", "shape", "number", "shading"])

def find_sets(cards):
    return [combo for combo in combinations(cards, 3) if is_set(*combo)]

def create_grid(image_paths):
    images = [Image.open(path) for path in image_paths]
    cell_width, cell_height = images[0].size
    grid_width = cell_width * 4
    grid_height = cell_height * 3
    grid_image = Image.new('RGB', (grid_width, grid_height))

    for index, img in enumerate(images):
        row = index // 4
        col = index % 4
        grid_image.paste(img, (col * cell_width, row * cell_height))

    img_byte_arr = io.BytesIO()
    grid_image.save(img_byte_arr, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')}"

def process_set(i):
    cards = generate_cards()
    sets = find_sets(cards)
    image_paths = [card.image for card in cards]
    grid_image = create_grid(image_paths)
    
    input_field = [
            {
                "role": "user",
                "content": [

                    {"type": "text", "text": "You are an AI assistant tasked with identifying a set in the card game Set. First, let me explain the rules of the game:\n\nSet is a card game where each card has four features:\n1. Number (One, Two, or Three)\n2. Shape (Diamond, Squiggle, or Oval)\n3. Shading (Filled, Shaded, or Empty)\n4. Color (Red, Green, or Purple)\n\nA set is made of 3 cards. Each card has 4 things to look at:\n\nShape (oval, squiggle, or diamond)\nColor (red, green, or purple)\nNumber (one, two, or three shapes)\nShading (solid, striped, or open)\n\nThe big rule: For each of these 4 things, the cards must be either ALL THE SAME or ALL DIFFERENT.\n\nExamples:\n\nGood Set:\n\n3 red cards (all same color)\nAll have different shapes (oval, squiggle, diamond)\nAll have two shapes (same number)\nAll are solid (same shading)\n\nAnother Good Set:\n\n3 different colors (red, green, purple)\n3 different shapes (oval, squiggle, diamond)\n3 different numbers (one, two, three)\n3 different shadings (solid, striped, open)\n\nBad Set:\n\n2 red cards and 1 green card (not all same, not all different)\nEverything else can be the same or different, but this is already not a set because of the colors\n\nRemember: It's okay if some things are the same and others are different, as long as each thing (color, shape, number, shading) follows the \"all same or all different\" rule.\n\nYour task is to analyze an image of 12 Set cards and identify a set. Use a scratchpad to think through your analysis, and then provide your final answer in a structured format.\n\nHere is an image of 12 set cards: \n\n"},
                    {"type": "image", "image": grid_image},
                    {"type": "text", "text": "\n\nInstructions:\n1. Analyze the image carefully, identifying the features of each card.\n2. Use a <scratchpad> to list out the features of each card, and then think step by step to identify potential sets. Think out loud and very carefully. Behave as if the scratchpad is a stream of consciousness, and feel free to correct and double check yourself in it. You can try again and again and again, as many times as you'd like. However, you should think before you identify a possible set based on what you see.\n3. Identify one possible set among the 12 cards.\n4. Provide your final answer in the following structured format:\n\n\n<answer>\n<set>\n<card1><number>[number]</number><color>[color]</color><shading>[shading]<shading><shape>[shape]</shape></card1>\n<card2>[Description of card 2]</card2>\n<card3>[Description of card 3]</card3>\n</set>\n</answer>\n\nDescribe each card using the format: [Number] [Color] [Shading] [Shape]\nFor example: \"<number>One</number> <color>Red</color> <shading>Filled</shading> <shape>Diamond</shape>\" or \"<number>Two</number> <color>Green</color> <shading>Shaded</shading> <shape>Oval</shape>\"\n\nDo not use plurals, use singular. For example, instead of Diamonds, say Diamond.\n\nIf there are no possible sets, your final answer should be:\n<answer>\n<set>\n</set>\n</answer>\n\nRemember to use the <scratchpad> tags for your analysis and the <answer> tags for your final, structured response. Do not include any explanations or additional text outside of these tags."}
                ]
            }
        ]

    target_field = []
    if sets:
        for set_combo in sets:
            # Generate all 6 permutations of the set
            for perm in permutations(set_combo):
                set_string = "<answer>\n<set>\n"
                for i, card in enumerate(perm, 1):
                    set_string += f"<card{i}>{card.to_string()}</card{i}>\n"
                set_string += "</set>\n</answer>"
                set_string = set_string.replace(" ", "")
                target_field.append(set_string)

    return {
        'set_id': i+1,
        'input': input_field,
        'target': target_field,
        'possible_sets': len(sets),
        'image_type': 'image/png'
    }

def main():
    output_file = 'set_game_data_old_prompt.jsonl'
    total_sets = 1000
    chunk_size = 100  # Process and save in chunks of 100

    # Check if file exists and load existing data
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = [json.loads(line) for line in f]
        start_id = max(item['set_id'] for item in existing_data) + 1
        print(f"Resuming from set_id {start_id}")
    else:
        existing_data = []
        start_id = 1

    # Use all available CPU cores
    with mp.Pool(mp.cpu_count()) as pool:
        with tqdm(total=total_sets, initial=start_id-1, desc="Overall Progress") as pbar:
            for chunk_start in range(start_id-1, total_sets, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_sets)
                chunk_size = chunk_end - chunk_start

                results = list(tqdm(pool.imap(process_set, range(chunk_start, chunk_end)), 
                                    total=chunk_size, 
                                    desc=f"Processing sets {chunk_start+1}-{chunk_end}",
                                    leave=False))

                # Append new results to existing data
                existing_data.extend(results)

                # Save updated data to jsonl
                with open(output_file, 'w') as f:
                    for item in existing_data:
                        json.dump(item, f)
                        f.write('\n')

                pbar.update(chunk_size)

    print(f"All data saved to {output_file}")

if __name__ == "__main__":
    main()