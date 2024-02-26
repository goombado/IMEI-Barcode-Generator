from xhtml2pdf import pisa
from barcode import Code128
from barcode.writer import ImageWriter
from base64 import b64encode as encode
from io import BytesIO
from datetime import datetime
from PIL import Image
import secrets
import json



class BarcodePrint:

    def __init__(self, user_str=None, cols=4):
        self.html_text = """
<!DOCTYPE html>
<html>
<head>
<style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    }
</style>
</head>
<body>

<table style='font-family:"sans-serif", Verdana, monospace; font-size:100%; width:80%'>

"""
        # self.pdf_path = f'output\\{datetime.now().strftime("IMEI_%d%m%Y_%H%M%S")}.pdf'
        self.pdf_path = f'output/{datetime.now().strftime("IMEI_%d%m%Y_%H%M%S")}.pdf'
        self.IMEI_names = {}
        self.IMEI_base64 = {}
        self.user_str = user_str
        self.cols = cols


    def IMEI_get_input(self):
        imei = input("Enter an IMEI (press Enter when done, or type \"exit\" to quit):\n").strip()

        while (imei != ''):
            if imei.lower() == "exit":
                return False

            if (len(imei) != 15):
                print("IMEI was not 15 digits long.")
                imei = input("Enter an IMEI (press Enter when done, or type \"exit\" to quit):\n").strip()
                continue

            name = input("Enter device's name:\n").strip()

            while name == '':
                name = input("Please enter a name for the device:\n").strip()

            self.IMEI_names[imei] = name

            print()
            imei = input("Enter an IMEI (press Enter when done, or type \"exit\" to quit):\n").strip()

        if len(self.IMEI_names.keys()) == 0:
            return False

        return True


    def IMEI_get_str(self):
        str = self.user_str
        str = str.replace('\r', '')
        imei_list = str.split(sep='\n')
        # imei_list = []

        # for elem in imei_list_raw:
        #     if elem != '':
        #         imei_list.append(elem)

        for i in range(len(imei_list)):
            try:
                if i % 2 == 0:
                    self.IMEI_names[imei_list[i]] = imei_list[i+1]
            except:
                break

        return True


    def IMEI_to_base64(self):
        # width_dict = {
        #     4: 0.35,
        #     3: 0.5,
        #     2: 0.7
        # }
        width_dict = {
            4: 1,
            3: 1.5,
            2: 2
        }
        # height_dict = {
        #     4: 2.5,
        #     3: 4,
        #     2: 8
        # }
        options = {
            # 'module_width': width_dict[self.cols],
            # 'module_height': height_dict[self.cols],
            'module_height': 3,
            'quiet_zone': 0,
            'text_distance': 1,
            'dpi': 600,
            'font_size': 18
        }
        for imei in self.IMEI_names.keys():
            b1 = BytesIO()
            b2 = BytesIO()
            Code128(imei, writer=ImageWriter()).write(b1, options=options)
            image = Image.open(b1)
            # cropped = image
            cropped = image.crop((0, 0, image.width, 150))
            cropped.thumbnail((int(cropped.width*(width_dict[self.cols])), 10000))
            cropped.save(b2, format="JPEG")
            barcode = encode(b2.getvalue()).decode()

            self.IMEI_base64[imei] = barcode


    def IMEI_to_base64_single(self, imei):
        # width_dict = {
        #     4: 0.35,
        #     3: 0.5,
        #     2: 0.7
        # }
        width_dict = {
            4: 1,
            3: 1.5,
            2: 2
        }
        font_dict = {
            4: 15,
            3: 20,
            2: 25
        }
        options = {
            # 'module_width': width_dict[self.cols],
            # 'module_height': height_dict[self.cols],
            'module_height': 3,
            'quiet_zone': 0,
            'text_distance': 1,
            'dpi': 600,
            'font_size': font_dict[self.cols]
        }

        b1 = BytesIO()
        b2 = BytesIO()
        Code128(imei, writer=ImageWriter()).write(b1, options=options)
        image = Image.open(b1)
        # cropped = image
        cropped = image.crop((0, 0, image.width, 150))
        cropped.thumbnail((int(cropped.width*(width_dict[self.cols])), 10000))
        cropped.save(b2, format="JPEG")
        barcode = encode(b2.getvalue()).decode()
        # print(cropped.size)
        try:
            image.close()
        except Exception as e:
            print(f'Close 1: {e}')

        try:
            cropped.close()
        except Exception as e:
            print(f'Close 1: {e}')

        return barcode



    def table_write(self):
        imei_set = self.IMEI_names.keys()
        i = 0

        width_dict = {
            4: 1,
            3: 1.5,
            2: 2
        }

        for imei in imei_set:
            temp = ''

            if i % self.cols == 0:
                temp += "<tr>\n"

            # temp += f"<td style=\"text-align:center\"><img src='data:image/jpeg;base64,{self.IMEI_base64[imei]}'; "
            temp += f"<td style=\"text-align:center\"><img src='data:image/jpeg;base64,{self.IMEI_to_base64_single(imei)}'; "
            temp += f"width={100*width_dict[self.cols]} /><br><b>{self.IMEI_names[imei]}</b></td>\n"

            if i % self.cols == self.cols - 1:
                temp += "</tr>\n"

            self.html_text += temp
            i += 1

        # print(i)
        # print(self.cols - i)
        # print("<td style=\"text-align:center\"></td>" * (self.cols - i))
        self.html_text += "<td style=\"text-align:center\"></td>" * (self.cols - i if i != 0 else 0)

        if i % self.cols != (self.cols - 1):
            self.html_text += "</tr>\n"


        self.html_text += "</table>\n"



    def html_final(self):
        self.html_text += "\n</body>\n</html>"


    def html_file_create(self):
        html_out = open("temp.html", "w")
        html_out.write(self.html_text)
        html_out.close()


    def html_to_pdf(self):
        outFile = open(self.pdf_path, "w+b")
        pisa_status = pisa.CreatePDF(self.html_text, dest=outFile)

        return pisa_status.err


    def main(self, cli=False):
        if cli:
            if (not self.IMEI_get_input()):
                print("Goodbye :)")
                return
        else:
            self.IMEI_get_str()

        # self.IMEI_to_base64()
        self.table_write()
        self.html_final()
        # self.html_file_create()
        err = self.html_to_pdf()

        if err:
            print("\nSomething went wrong :(")
        else:
            if cli:
                print(f"\nPDF saved to {self.pdf_path}")
                return
            else:
                f = open('tokens.json')
                tokens = json.load(f)
                f.close()
                token = secrets.token_urlsafe(32)
                tokens[token] = self.pdf_path
                f = open('tokens.json', 'w')
                json.dump(tokens, f, indent=4)
                f.close()
                return token
                # return self.pdf_path

