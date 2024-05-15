import socket

import zpl
from django.conf import settings


class BarcodePrinter:
    def __init__(self):
        self.printer_ip_address = settings.PRINTER_IP_ADDRESS

    def generate_label(self, sample_id):
        """
        Generate a ZPL label for a given sample ID
        """
        lbl = zpl.Label(100, 60)
        height = 0
        lbl.origin(0, height)
        lbl.write_barcode(height=50, barcode_type=zpl.barcode.CODE128,
                          check_digit=zpl.barcode.CHECK_DIGIT_NO)
        lbl.write_text(f"Sample ID: {sample_id}", char_height=10, char_width=8,
                       line_width=60, justification='C')
        lbl.endorigin()

        return lbl.dumpZPL()

    def print_zpl(self, zpl_string):
        """
        Send the ZPL string to the printer
        """
        PORT = settings.PORT

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.printer_ip_address, PORT))
            sock.send(bytes(zpl_string, 'utf-8'))

    def print_barcode_for_selected_samples(self, selected_samples):
        """
        Generate the barcode label for each selected sample and send them to the printer
        """
        for sample_id in selected_samples:
            label = self.generate_label(sample_id)
            self.print_zpl(label)
