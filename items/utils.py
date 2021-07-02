# this function lets you generate pdf from plz command: Below you can see the order of arguments
# [0] = barcode
# [1] = sender_name
# [2] = sender_city
# [3] = weight
# [4] = receiver_name
# [5] = receiver_number
# [6] = receiver_city
# [7] = date
# [8] = company_name
def generate_zpl(*args):

    text = f'^XA^FX First section with bar code.\
    ^BY4,3,200^FO50,25^BC^FD{args[0]}^FS \
    ^FO0,370^GB900,3,3^FS \
    ^FX Second section with sender address and permit information. \
    ^CFA,30 \
    ^FO50,400^FDSender:^FS \
    ^CFA,40 \
    ^FO50,440^FD{args[1]}^FS \
    ^CFA,30 \
    ^CFA,30 \
    ^FO50,520^FDSender City:^FS \
    ^CFA,45 \
    ^FO50,560^FD{args[2]}^FS \
    ^CFA,30 \
    ^FO600,400^GB160,160,4^FS \
    ^FO620,440^FDWeight:^FS \
    ^FO620,490^FD{args[3]} kg^FS \
    ^FO0,620^GB900,3,3^FS \
    ^FX Third section with receiver. \
    ^CFA,30 \
    ^FO50,630^FDReceiver:^FS \
    ^CFA,40 \
    ^FO50,675^FD{args[4]}^FS \
    ^FO50,745^FD{args[5]}^FS \
    ^CFA,50 \
    ^FO50,810^FD{args[6]}^FS ^FO49,810^FD{args[6]}^FS \
    ^FO48,810^FD{args[6]}^FS ^FO51,810^FD{args[6]}^FS \
    ^FO0,880^GB900,3,3^FS \
    ^FX Fourth section (the two boxes on the bottom). \
    ^FO25,910^GB750,250,2^FS \
    ^CF0,40 \
    ^FO70,970^FDShipping Date^FS \
    ^CF0,40 \
    ^FO70,1020^FD{args[7]}^FS \
    ^CF0,40 \
    ^FO500,970^FDCompany:^FS \
    ^CF0,65 \
    ^FO500,1020^FD{args[8]}^FS \
    ^XZ'

    return text
