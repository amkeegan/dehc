import qrcode #python -m pip install qrcode
from qrcode.image.styledpil import StyledPilImage
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from barcode import EAN13 #python -m pip install python-barcode[images]
from barcode.writer import ImageWriter
from barcode import generate
from barcode import Code128
from io import BytesIO

import math

class IDCardBuilder:

    id_card_dimensions = (640,1006) ## Target ID Card dimensions in pixels

    ## _position = (x,y,width,height)
    tag_position = (
        int(id_card_dimensions[0]*0.05),
        int(id_card_dimensions[0]*0.05),
        int(id_card_dimensions[0]*0.15),
        int(id_card_dimensions[1]*0.40),
    )
    portrait_position = (
        int(tag_position[0] + tag_position[2] + (id_card_dimensions[0] * 0.05)),
        int(tag_position[1]),
        int(id_card_dimensions[0] * 0.5),
        int(id_card_dimensions[1] * 0.4)
    )
    qrcode_position = (
        int(id_card_dimensions[0] * 0.05),
        int(id_card_dimensions[1] - (id_card_dimensions[0] * 0.4) - (id_card_dimensions[0] * 0.05)),
        int(id_card_dimensions[0] * 0.4),
        int(id_card_dimensions[0] * 0.4)
    )
    logo_position = (
        int(id_card_dimensions[0] * 0.4 + id_card_dimensions[0] * 0.05 + id_card_dimensions[0] * 0.1),
        int(id_card_dimensions[1] - (id_card_dimensions[0] * 0.4) - (id_card_dimensions[0] * 0.05)),
        int(id_card_dimensions[0] * 0.4),
        int(id_card_dimensions[0] * 0.4)
    )
    textblock_position = (
        int(tag_position[0]),
        int(id_card_dimensions[0] * 0.05 + tag_position[3] + id_card_dimensions[0] * 0.05),
        int(id_card_dimensions[0] * 0.70),
        int(id_card_dimensions[1] - 4 * id_card_dimensions[0] * 0.05 - qrcode_position[3] - tag_position[3])
    )
    barcode_position = (
        int(portrait_position[0] + portrait_position[2] + id_card_dimensions[0] * 0.05),
        int(id_card_dimensions[0] * 0.05),
        int(id_card_dimensions[0] * 0.15),
        int(id_card_dimensions[1] * 0.4 + textblock_position[3] + id_card_dimensions[0] * 0.05)
    )

    name_font = ImageFont.truetype('arialbd.ttf', 40)

    DOB_font = ImageFont.truetype('arial.ttf', 30)

    font = ImageFont.truetype('arial.ttf', 40)

    def makeQRCode(self, qrcode_id, embedded_logo_path = None):
        ## Make QR Code
        qr = qrcode.QRCode(
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            version=None,
            #box_size=1
            border=0 #Technically out of spec, but we have a buffer 5% card width in play
        )

        qr.add_data(qrcode_id)

        qr.make(fit=True)

        qrcode_image = qr.make_image(
            image_factory=StyledPilImage, 
            embeded_image_path=embedded_logo_path,
        )

        qrcode_image = qrcode_image.resize((self.qrcode_position[2], self.qrcode_position[3]))

        return qrcode_image

    def addQRCodeImage(self, qrcode_image, id_card):
        id_card.paste(
            qrcode_image, 
            (
                self.qrcode_position[0],
                self.qrcode_position[1],
                self.qrcode_position[0] + self.qrcode_position[2],
                self.qrcode_position[1] + self.qrcode_position[3]
            )
        )

    def makeBarcode(self,barcode_id):
        ## Make barcode
        fp = BytesIO()

        generate(
            name='code128', 
            code=barcode_id, 
            writer=ImageWriter(), 
            output=fp,
            #writer_options={"module_height": 7},
            text=''
        )

        barcode_image = Image.open(fp)

        barcode_image = barcode_image.resize(
            (
                self.barcode_position[3], #Flipped 2,3 for rotation below
                self.barcode_position[2]
            )
        )

        # barcode_image = barcode_image.resize(
        #     barcode_image.size[0] * 2,
        #     barcode_image.size[1] * 2
        # )

        barcode_image = barcode_image.rotate(90, expand=1)

        return barcode_image

    def addBarcodeImage(self, barcode_image, id_card):
        id_card.paste(
            im=barcode_image, 
            box=(
                    self.barcode_position[0],
                    self.barcode_position[1]
                )
        )

    def makePortraitImage(self, portrait: Image):
        ## This step shouldn't be need normally
        ##  Normally the source image will be larger than the hole
        ##  This step allows the thumbnail step to reduce size and maintain aspect ratios
        portrait = portrait.resize(
            (
                portrait.size[0]*4, 
                portrait.size[1]*4
            )
        )

        portrait.thumbnail(
            size=(
                self.portrait_position[2],
                self.portrait_position[3]
            ),
            resample=Image.ANTIALIAS
        )
        return portrait

    def addPortraitImage(self, portrait_image, id_card):
        midPoint_x = int(self.portrait_position[0] + self.portrait_position[2] / 2)
        thumbnail_x = int(midPoint_x - (portrait_image.size[0] / 2))

        midPoint_y = int(self.portrait_position[1] + self.portrait_position[3] / 2)
        thumbnail_y = int(midPoint_y - (portrait_image.size[1] / 2))

        id_card.paste(
            im=portrait_image, 
            box=(
                thumbnail_x,
                thumbnail_y
                #portrait_position[0] + portrait_position[2],
                #portrait_position[1] + portrait_position[3]
            )
        )

    def makeLogoImage(self, logo: Image):
        logo = logo.resize(
            (
                logo.size[0] * 4,
                logo.size[1] * 4
            )
        )

        logo.thumbnail(
            size=(
                self.logo_position[2],
                self.logo_position[3]
            ),
            resample=Image.ANTIALIAS
        )
        return logo

    def addLogoImage(self, logo_image, id_card):
        midPoint_x = int(self.logo_position[0] + self.logo_position[2] / 2)
        thumbnail_x = int(midPoint_x - (logo_image.size[0] / 2))

        midPoint_y = int(self.logo_position[1] + self.logo_position[3] / 2)
        thumbnail_y = int(midPoint_y - (logo_image.size[1] / 2))

        id_card.paste(
            logo_image,
            (
                thumbnail_x,
                thumbnail_y
            ),
        )

    def drawText(self, draw, font_y, midPoint_x, text, font):
        text_width, text_height = font.getsize(text)

        draw.text(
            (
                midPoint_x - int(text_width / 2),
                font_y
            ),
            text,
            (0,0,0),
            font=font
        )

        font_y += text_height

        return font_y

    def addTextAll(self, id_card, bold_text, normal_texts):
        ## Add some text
        draw = ImageDraw.Draw(id_card)

        font_y = self.textblock_position[1]

        midPoint_x = int(self.textblock_position[0] + self.textblock_position[2] / 2)

        font_y = self.drawText(draw, font_y, midPoint_x, bold_text, self.name_font)
        for text in normal_texts:
            font_y = self.drawText(draw, font_y, midPoint_x, text, self.DOB_font)

    def makeTagText(self, text):
        box_text_width, box_text_height = self.font.getsize(text)

        box_text_image = Image.new(
            'RGBA', 
            (box_text_width, box_text_height),
            (255,255,255)
        )

        draw = ImageDraw.Draw(box_text_image)

        draw.text((0,0), text=text, font=self.font, fill=(0,0,0, 255))

        box_text_image = box_text_image.rotate(90, expand=1)

        box_text_image = box_text_image.resize(
            (
                box_text_image.size[0] * 2,
                box_text_image.size[1] * 2
            )
        )

        box_text_image.thumbnail(
            (
                self.tag_position[2],
                self.tag_position[3]
            ),
            resample=Image.ANTIALIAS
        )
        return box_text_image

    def addTagTextImage(self, tag_image, id_card):
        midPoint_x = int(self.tag_position[0] + self.tag_position[2] / 2)
        thumbnail_x = int(midPoint_x - (tag_image.size[0] / 2))

        midPoint_y = int(self.tag_position[1] + self.tag_position[3] / 2)
        thumbnail_y = int(midPoint_y - (tag_image.size[1] / 2))


        id_card.paste(
            tag_image,
            (
                thumbnail_x,
                thumbnail_y
            )
        )

    def addWaterMark(self, id_card):
        ## Add some rotated watermark, courtesy: https://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
        watermark_text = 'DRAFT'
        watermark_text_length = len(watermark_text)

        FONT_RATIO = 1
        DIAGONAL_PCT = 1

        diagonal_length = int(
            math.sqrt(
                (id_card.size[0]**2) + (id_card.size[1]**2)
            )
        )

        diagonal_to_use = diagonal_length * DIAGONAL_PCT

        font_size = int(diagonal_length / (watermark_text_length / FONT_RATIO))
        font = ImageFont.truetype('arial.ttf', font_size)
        
        opacity = int(256 * 0.50)

        watermark_width, watermark_height = font.getsize(watermark_text)

        watermark_image = Image.new(
            'RGBA', 
            (watermark_width, watermark_height),
            (0,0,0,0)
        )

        draw = ImageDraw.Draw(watermark_image)

        draw.text((0,0), text=watermark_text, font=font, fill=(0,0,0, opacity))

        angle = math.degrees(math.atan(id_card.size[1]/id_card.size[0]))

        watermark_image = watermark_image.rotate(angle, expand=1)

        wx, wy = watermark_image.size
        px = int((id_card.size[0] - wx) / 2)
        py = int((id_card.size[1] - wy) / 2)
        id_card.paste(watermark_image, (px, py, px + wx, py + wy), watermark_image)

    def addOutline(self, outlines, position, color):
        outlines.rectangle(
            (
                position[0],
                position[1],
                position[0] + position[2],
                position[1] + position[3]
            ),
            outline=color
        )

    def addOutlines(self, id_card):

        id_card_outlines = ImageDraw.Draw(id_card)
        
        self.addOutline(id_card_outlines, self.barcode_position, 'red')
        self.addOutline(id_card_outlines, self.portrait_position, 'red')
        self.addOutline(id_card_outlines, self.tag_position, 'red')
        self.addOutline(id_card_outlines, self.textblock_position, 'red')
        self.addOutline(id_card_outlines, self.qrcode_position, 'red')
        self.addOutline(id_card_outlines, self.logo_position, 'red')

    def generateIDCard(self, qrcode_id, embedded_logo_path, barcode_id, name, secondary_texts, tag_text, logo, portrait, save_path):
 
        id_card = Image.new('RGB', self.id_card_dimensions, color=(255,255,255))
        
        qrcode_image = self.makeQRCode(qrcode_id, embedded_logo_path)
        self.addQRCodeImage(qrcode_image, id_card)

        barcode_image = self.makeBarcode(barcode_id)
        self.addBarcodeImage(barcode_image, id_card)

        portrait_image = self.makePortraitImage(portrait)
        self.addPortraitImage(portrait_image, id_card)

        tag_image = self.makeTagText(tag_text)
        self.addTagTextImage(tag_image, id_card)

        logo_image = self.makeLogoImage(logo)
        self.addLogoImage(logo_image, id_card)

        self.addTextAll(id_card, name, secondary_texts)

        # Outlines only useful for debug / adjusting element positions
        #self.addOutlines(id_card)

        id_card.show()

        id_card.save(save_path)    

        return id_card

if __name__ == "__main__":

    qrcode_id = 'Person/JoeCarter'
    barcode_id = 'Person/JoeCarter'
    fullname = 'Joe Carter'
    dob = '30-SEP-1965'
    nationality = 'Nationality: British'
    tag = 'Exercise: City of Fire'
    embedded_logo_path = 'ir-logo.png'
    portrait = Image.open('Joe_Carter.png')
    logo = Image.open('ir.png')
    filename = 'JoeCarter_ID.png'

    cardBuilder = IDCardBuilder()

    new_card = cardBuilder.generateIDCard(qrcode_id, embedded_logo_path, barcode_id, fullname, (dob,nationality), tag, logo, portrait, filename)
    
    print('Done')