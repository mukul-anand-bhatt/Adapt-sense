# conversion.py
braille = ['⠴','⠂','⠆','⠒','⠲','⠢','⠖','⠶','⠦','⠔',
           '⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚',
           '⠅','⠇','⠍','⠝','⠕','⠏','⠟','⠗','⠎','⠞',
           '⠥','⠧','⠺','⠭','⠽','⠵',
           '⠱','⠰','⠣','⠿','⠀','⠮','⠐','⠼','⠫','⠩',
           '⠯','⠄','⠷','⠾','⠡','⠬','⠠','⠤','⠨','⠌',
           '⠜','⠹','⠈','⠪','⠳','⠻','⠘','⠸']

english = ['0','1','2','3','4','5','6','7','8','9',
           'a','b','c','d','e','f','g','h','i','j',
           'k','l','m','n','o','p','q','r','s','t',
           'u','v','w','x','y','z',
           ':',';','<','=',' ','!','"','#','$','%',
           '&','','(',')','*','+',',','-','.','/',
           '>','?','@','[','\\',']','^','_']

# Creating mappings
english_to_braille = dict(zip(english, braille))
braille_to_english = dict(zip(braille, english))

def convert_to_braille(text: str) -> str:
    """Convert English text to Braille."""
    return ''.join(english_to_braille.get(char.lower(), char) for char in text)

def convert_to_english(text: str) -> str:
    """Convert Braille text to English."""
    return ''.join(braille_to_english.get(char, char) for char in text)
