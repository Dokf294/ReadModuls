from PIL import Image 

TableAscii = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

def PHOTO_TO_ASCII(imagePath): 
    img = Image.open(imagePath)
    old_width, old_height = img.size 
    ratio = old_height / old_width 
    new_height, new_width = int(100 * ratio), 100 
    img = img.resize((new_width, new_height)) 
    img = img.convert('L') 
    
    pixels = img.getdata()  
    asciiArt = ''  

    for pixelValues in pixels: 
        asciiArt += TableAscii[pixelValues // 25] 

    asciiStr = '\n'.join([asciiArt[i:i+new_width] for i in range(0, len(asciiArt), new_width)]) 

    return asciiStr 

def PHOTO_RESULT(Photo): 
    with open('ResultPhoto.txt', 'w') as f: 
        f.write(Photo) 
        print('write successe!') 

if __name__ == '__main__': 
    PHOTO_RESULT('simpleExample.png')

