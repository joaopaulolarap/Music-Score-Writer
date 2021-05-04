import cv2
import numpy as np
import math
import os             

'''
Numbers refering to the notes (%12):
0 -> B
1 -> C
2 -> C#
3 -> D
4 -> D#
5 -> E
6 -> F
7 -> F#
8 -> G
9 -> G#
10 -> A
11 -> A#

Numbers refering to the rests:
50 -> Whole rest
51 -> Half rest
52 -> Quarter rest
53 -> Eight rest
54 -> Sixteenth rest

Line jump in pixels -> 178
'''

line_jump = 178

class Note:
    
    def __init__(self, note, duration, note2 = -1, note3 = -1, note4 = -1, note5 = -1, note6 = -1):

        self.note = []
        self.note.append(note)
        self.note.append(note2)
        self.note.append(note3)
        self.note.append(note4)
        self.note.append(note5)
        self.note.append(note6)
        self.duration = duration
        self.connected = False
        self.nref = None
        self.pref = None

#An object of this class will hold the ensamble of notes and the characteristics of the piece
class Score:
    
    def __init__(self, BPM, compass1, compass2, KS, sharp):

        self.n_notes = 0
        self.BPM = BPM
        self.KS = KS
        self.sharp = sharp
        self.compass1 = compass1
        self.compass2 = compass2
        self.Note_List_Head = None

    def insert_note(self, note, duration, note2 = -1, note3 = -1, note4 = -1, note5 = -1, note6 = -1):

        self.n_notes = self.n_notes + 1

        if self.Note_List_Head is None:

            new_note = Note(note, duration, note2, note3, note4, note5, note6)
            self.Note_List_Head = new_note
            print("Note inserted")
            return

        n = self.Note_List_Head
        while n.nref is not None:
            n = n.nref
        new_note = Note(note, duration, note2, note3, note4, note5, note6)
        n.nref = new_note
        new_note.pref = n
        print("Note inserted")

#Objects of this class will hold the vectors of a given symbol as well as its lenght, read from a text file
class Symbols:

    def __init__(self, symbol_file):

        #Symbol vectors:
        self.x, self.y, self.len = self.get_symbol(symbol_file)

    def get_symbol(self, symbol_file):
        
        f = open(symbol_file, "r")
        symbol_x, symbol_y = [], []
        for l in f:
            row = l.split()
            symbol_x.append(row[0])
            symbol_y.append(row[1])
        lenght = len(symbol_x)
        return symbol_x, symbol_y, lenght

class Create_Image:

    def __init__(self, score):

        self.img_sheet = cv2.imread('pautas-1.jpg')
        self.score = score
        self.note_count = 0
        self.durations_count = 0
        self.compass_count = 1
        self.line_count = 0
        self.page_count = 1
        self.starting_offsetX = 187
        self.starting_offsetY = 150
        self.pixel_offsetX = self.starting_offsetX
        self.pixel_offsetY = self.starting_offsetY

        #Key Signature:
        self.A_sharp = False
        self.B_sharp = False
        self.C_sharp = False
        self.D_sharp = False
        self.E_sharp = False
        self.F_sharp = False
        self.G_sharp = False

        #Symbol vectors:

        all_files = os.listdir("Symbol Arrays/")
        print(all_files)

        #Clefs:
        self.treble_clef = Symbols("treble_array.txt")

        #Notes and pauses:
        self.quarter_note_up = Symbols(all_files[17])
        self.quarter_note_down = Symbols(all_files[16])
        self.quarter_rest = Symbols(all_files[18])
        self.eight_note_up = Symbols(all_files[9])
        self.eight_note_down = Symbols(all_files[7])
        self.eight_rest = Symbols(all_files[8])
        self.half_note_up = Symbols(all_files[12])
        self.half_note_down = Symbols(all_files[11])
        self.half_rest = Symbols(all_files[13])
        self.whole_note = Symbols(all_files[25])
        self.whole_rest = Symbols(all_files[26])
        self.sixteenth_note_up = Symbols(all_files[23])
        self.sixteenth_note_down = Symbols(all_files[21])
        self.sixteenth_rest = Symbols(all_files[22])

        #miscellaneous
        self.sharp = Symbols(all_files[20])
        self.natural = Symbols(all_files[14])
        self.flat = Symbols(all_files[10])
        self.note_head = Symbols(all_files[15])
        self.dot = Symbols(all_files[6])

        #Time Signature (TS) numbers
        self.two_TS = Symbols(all_files[0])
        self.three_TS = Symbols(all_files[1])
        self.four_TS = Symbols(all_files[2]) 
        self.six_TS = Symbols(all_files[3])
        self.seven_TS = Symbols(all_files[4])
        self.eight_TS = Symbols(all_files[5])
        

    #Draws the clef and key signature in every line, as well as the time signature in the first line
    def setup_clef_TS(self):

        draw_clef = self.treble_clef

        #Gets the Time Signature numbers
        if(self.score.compass1 == 2):
            draw_TS1 = self.two_TS
        elif(self.score.compass1 == 3):
            draw_TS1 = self.three_TS
        elif(self.score.compass1 == 4):
            draw_TS1 = self.four_TS
        elif(self.score.compass1 == 6):
            draw_TS1 = self.six_TS
        elif(self.score.compass1 == 7):
            draw_TS1 = self.seven_TS
        elif(self.score.compass1 == 8):
            draw_TS1 = self.eight_TS

        if(self.score.compass2 == 2):
            draw_TS2 = self.two_TS
        elif(self.score.compass2 == 3):
            draw_TS2 = self.three_TS
        elif(self.score.compass2 == 4):
            draw_TS2 = self.four_TS
        elif(self.score.compass2 == 6):
            draw_TS2 = self.six_TS
        elif(self.score.compass2 == 7):
            draw_TS2 = self.seven_TS
        elif(self.score.compass2 == 8):
            draw_TS2 = self.eight_TS

        if(self.score.sharp == True):
            draw_KS = self.sharp
        else:
            draw_KS = self.flat

        #Gets the Key Signature from the 'score' object in this class
        self.get_note_modifiers()

        #Draws the clef and Key Signature in every "line"
        for j in range (12):

            #Clef
            for i in range (draw_clef.len):
                self.img_sheet[self.pixel_offsetX + int(draw_clef.x[i]) + j * line_jump][self.pixel_offsetY + int(draw_clef.y[i])] = [0,0,0]

            #Key Signature
            for i in range (draw_KS.len):
                for k in range(self.score.KS):
                    shift_x = self.get_KS_shifts(k)
                    self.update_offsets(shift_x, 0)
                    self.img_sheet[self.pixel_offsetX + int(draw_KS.x[i]) + j * line_jump + 10][self.pixel_offsetY + int(draw_KS.y[i])] = [0,0,0] #+10 pra ajuste de offset vertical
                    self.update_offsets(0, 15)
                self.pixel_offsetX = self.starting_offsetX
                self.update_offsets(0, -15*self.score.KS)


        self.update_offsets(0, 15 * self.score.KS) #15 is the lenght of a sharp symbol, in pixels
        
        #Draws the numbers from the Time Signature
        for i in range (draw_TS1.len):
            self.img_sheet[self.pixel_offsetX + int(draw_TS1.x[i]) + 10][self.pixel_offsetY + int(draw_TS1.y[i])] = [0,0,0] #+10 pra ajuste de offset vertical
        for i in range (draw_TS2.len):
            self.img_sheet[self.pixel_offsetX + int(draw_TS2.x[i]) + 45][self.pixel_offsetY + int(draw_TS2.y[i])] = [0,0,0] #+45 = 10 do ajuste + 35 tamanho da imagem

        #Updates the starting pixel for the drawing of the notes
        self.starting_offsetX = 267
        self.update_offsets(80, 48)

    #Registers the key signature
    def get_note_modifiers(self):

        self.F_sharp = False
        self.C_sharp = False
        self.G_sharp = False
        self.D_sharp = False
        self.A_sharp = False
        self.E_sharp = False
        self.B_sharp = False

        if(self.score.sharp == True):
             
            if(self.score.KS > 0):
                self.F_sharp = True

            if(self.score.KS > 1):
                self.C_sharp = True

            if(self.score.KS > 2):
                self.G_sharp = True       

            if(self.score.KS > 3):
                self.D_sharp = True

            if(self.score.KS > 4):
                self.A_sharp = True

            if(self.score.KS > 5):
                self.E_sharp = True

            if(self.score.KS > 6):
                self.B_sharp = True

        else:

            if(self.score.KS > 0):
                self.B_sharp = -1

            if(self.score.KS > 1):
                self.E_sharp = -1

            if(self.score.KS > 2):
                self.A_sharp = -1       

            if(self.score.KS > 3):
                self.D_sharp = -1

            if(self.score.KS > 4):
                self.G_sharp = -1

            if(self.score.KS > 5):
                self.C_sharp = -1

            if(self.score.KS > 6):
                self.F_sharp = -1


    #Gets the vertical shift between each Key Signature symbol
    def get_KS_shifts(self, k):

        if(self.score.sharp == True):
            
            if(k == 0):
                shift_x = 0

            elif(k == 1 or k == 3 or k == 4 or k == 6):
                shift_x = 27

            elif(k == 2 or k == 5):
                shift_x = -36

            return shift_x

        else:

            if(k == 0):
                shift_x = 48

            elif(k == 1 or k == 3 or k == 5):
                shift_x = -27

            elif(k == 2 or k == 4 or k == 6):
                shift_x = 36

            return shift_x

    #Updates the position of the current pixel in the image sweep
    def update_offsets(self, dx, dy):
        self.pixel_offsetX = self.pixel_offsetX + dx
        self.pixel_offsetY = self.pixel_offsetY + dy

    #Updates number of notes
    def update_note(self, n):
        self.note_count = n

    #Updates the duration count in a measure
    def update_durations(self, d):
        self.durations_count = d

    #Updates the bar count in a line
    def update_compass(self, c):
        self.compass_count = c

    #Updates the line count in a page
    def update_line(self, l):
        self.update_compass(1)
        self.line_count = l

    #Updates page count
    def update_page(self):
        self.update_line(0)
        self.page_count = self.page_count + 1

    #Sweeps the notes of the score, drawing all the symbols accordingly
    def sweep_score(self):

        n = self.score.Note_List_Head

        connection_direction = 0
        
        while n.nref is not None:

            print(self.compass_count)

            next_line = False
            next_compass = False    

            #Defines the horizontal space between notes (in pixels)
            if(self.line_count == 0):
                pixels_p_compass = math.floor((1510 - 80 - 70 - 15 * self.score.KS)/3) #80 pixels for the clef, 70 for the TS numbers and 15*n from the KS
            else:
                pixels_p_compass = math.floor((1510 - 80 - 15 * self.score.KS)/3) #No TS numbers in the other lines
            min_shift = math.floor(pixels_p_compass * self.score.compass2/(16 * self.score.compass1)) #Minimum horizontal space between symbols 
            shift = min_shift * n.duration * 8 #Proportional to the duration of the note

            #Space before note
            self.update_offsets(0, int(shift))
            
            #Updates the number of total notes drawn and total duration of the bar
            self.update_note(self.note_count + 1)
            self.update_durations(self.durations_count + n.duration)

            print(self.durations_count)

            if (self.durations_count >= self.score.compass1 / self.score.compass2):
                
                self.update_compass(self.compass_count + 1)
                next_compass = True
                
            if (self.compass_count > 3):
                
                self.update_line(self.line_count + 1)
                next_line = True 
                
            if (self.line_count > 12):
                self.update_page()


            #Checks if the notes will be connected, if yes connects them, and gets the parameters of the connecting bar
            r, bar_a, bar_x, bar_y = self.connect_if_necessary(n, min_shift, next_line)

            #Registers the direction of the connection
            if (n.connected == True and r != 0):
                connection_direction = r

            if (n.connected == False):
                connection_direction = 0

            #Checks the need of lower duration connections and connects all the notes needed. Called once for a whole set of connected notes
            if(r != 0):
                self.check_more_connections(bar_x, bar_y, bar_a, n, r, min_shift)

                for c in range(6):#All the simultaneous notes
                    if n.note[c] != -1:
                        
                        #Draws the note stems of the connected notes
                        self.draw_note_stem(bar_x, bar_y, bar_a, n, r, min_shift, c)

            #Draws the note symbol of all simultaneous notes
            for c in range(6):#All the simultaneous notes
                    if n.note[c] != -1:
                        self.draw_symbol(n, connection_direction, c)

            #space after note
            self.update_offsets(0, int(shift))

            if(next_compass == True):

                #MUDOU DE LUGAR. AINDA EM AVALIAÇÃO
                self.update_durations(0)

                #Draw the line dividing the bars

                self.update_offsets(0, 19) #space of the lenght of note head in pixels
                
                for i in range (70):
                    for j in range (2):
                        self.img_sheet[self.pixel_offsetX - i][self.pixel_offsetY + j] = [0,0,0]

                self.update_offsets(0, 10) #extra space after bar

                #Resets the accident changes in the compass              
                self.get_note_modifiers()

            if (next_line == True):
                
                self.starting_offsetX = self.starting_offsetX + line_jump
                self.starting_offsetY = 150 + 15 * self.score.KS
                self.update_offsets(self.starting_offsetX - self.pixel_offsetX, self.starting_offsetY - self.pixel_offsetY)
            
            n = n.nref

    def draw_symbol(self, n, connection_direction, c):

        #Takes the upside-down note depending on the note position
        if(n.note[c] > 22 and n.note[c] < 37):
            if (n.duration == 0.5 or n.duration == 0.75 or n.duration == 0.875):
                draw = self.half_note_down
            if (n.duration == 0.25 or n.duration == 0.375 or n.duration == 0.4375):
                draw = self.quarter_note_down
            if (n.duration == 0.125 or n.duration == 0.1875 or n.duration == 0.21875):
                draw = self.eight_note_down
            if (n.duration == 0.0625 or n.duration == 0.09375 or n.duration == 0.109375):
                draw = self.sixteenth_note_down

        #Takes the upside note depending on the note position
        elif (n.note[c] < 23):
            if (n.duration == 0.5 or n.duration == 0.75 or n.duration == 0.875):
                draw = self.half_note_up
            if (n.duration == 0.25 or n.duration == 0.375 or n.duration == 0.4375):
                draw = self.quarter_note_up
            if (n.duration == 0.125 or n.duration == 0.1875 or n.duration == 0.21875):
                draw = self.eight_note_up
            if (n.duration == 0.0625 or n.duration == 0.09375 or n.duration == 0.109375):
                draw = self.sixteenth_note_up

        #Takes the pauses
        elif (n.note[c] == 50):
            draw = self.whole_rest
        elif (n.note[c] == 51):
            draw = self.half_rest
        elif (n.note[c] == 52):
            draw = self.quarter_rest
        elif (n.note[c] == 53):
            draw = self.eight_rest
        elif (n.note[c] == 54):
            draw = self.sixteenth_rest

        #Takes the whole note (position independent)
        if (n.duration == 1 and n.note[c] < 50):
            draw = self.whole_note

        #Checks if it's a dotted note
        if (n.duration == 0.75 or n.duration == 0.375 or n.duration == 0.1875 or n.duration == 0.09375):
            dot = 1
        elif (n.duration == 0.875 or n.duration == 0.4375 or n.duration == 0.21875 or n.duration == 0.109375):
            dot = 2
        else:
            dot = 0

        #Takes the symbol of the note head for the notes that will be connected
        if(n.connected == True or c > 0):
            draw = self.note_head

        #Gets the vertical position of the note and a flag that indicates the need of a pitch-altering symbol
        shift, sharp_flag = self.get_shifts_treble(n, c)

        #Draws the corresponding symbol if necessary
        if(self.check_modifier_necessity(n.note[c], sharp_flag) == True):

            self.update_offsets(0, -15)

            if(sharp_flag == True):
                
                draw_modifier = self.sharp
                x_corrector = -9
                y_corrector = 0

            elif(sharp_flag == False):

                draw_modifier = self.natural
                x_corrector = 9
                y_corrector = 0

            else:

                draw_modifier = self.flat
                x_corrector = 9
                y_corrector = 0

            for i in range (draw_modifier.len):
                self.img_sheet[self.pixel_offsetX + int(draw_modifier.x[i]) + shift + x_corrector][self.pixel_offsetY + int(draw_modifier.y[i]) + y_corrector] = [0,0,0]

            self.update_offsets(0, 15)

        #Draws the complementary lines if needed
        if(shift <= -81 or shift >= 27):
            self.draw_complementary_lines(shift)

        #Draws the note/rest symbol
        for i in range (draw.len):
            self.img_sheet[self.pixel_offsetX + int(draw.x[i]) + shift][self.pixel_offsetY + int(draw.y[i])] = [0,0,0]

        #Draws the dot(s) if needed
        if(dot > 0):
            draw_dot = self.dot
            for j in range (dot):
                for i in range (draw_dot.len):
                    self.img_sheet[self.pixel_offsetX + int(draw_dot.x[i]) + shift - 8][self.pixel_offsetY + int(draw_dot.y[i]) + 25 + 6 * j] = [0,0,0] #25 -> lenght of note head + small space for the dot to be drawn (in pixels).

    #Gets the vertical shifts for the notes when the clef is the treble clef
    def get_shifts_treble(self, n, c):

        sharp_flag = False

        if(n.note[c] < 13):
            shift_fixed = 63

        elif(n.note[c] > 12 and n.note[c] < 25):
            shift_fixed = 0

        elif(n.note[c] > 24 and n.note[c] < 37):
            shift_fixed = -63

        elif(n.note[c] > 36 and n.note[c] < 49):
            shift_fixed = -126

        elif(n.note[c] == 50):
            shift_fixed = -25

        else:
            shift_fixed = -18

        note_code = n.note[c] % 12

        if(self.score.sharp == True):

            if(note_code == 1 or note_code == 2):
                a = 3

            elif(note_code == 3 or note_code == 4):
                a = 2

            elif(note_code == 5):
                a = 1

            elif(note_code == 6 or note_code == 7):
                a = 0

            elif(note_code == 8 or note_code == 9):
                a = -1

            elif(note_code == 10 or note_code == 11):
                a = -2

            elif(note_code == 0):
                a = -3

        else:

            if(note_code == 1):
                a = 3

            elif(note_code == 2 or note_code == 3):
                a = 2

            elif(note_code == 4 or note_code == 5):
                a = 1

            elif(note_code == 6):
                a = 0

            elif(note_code == 7 or note_code == 8):
                a = -1

            elif(note_code == 9 or note_code == 10):
                a = -2

            elif(note_code == 11 or note_code == 0):
                a = -3

        #if it's a rest, the varying shift is zero
        if(n.note[c] > 48):
            a = 0

        if(note_code == 2 or note_code == 4 or note_code == 7 or note_code == 9 or note_code == 11):
            if(self.score.sharp == True):
                sharp_flag = True
            else:
                sharp_flag = -1

        shift = 9 * a + shift_fixed

        return shift, sharp_flag

    #Checks the necessity of adding a pitch-altering symbol
    def check_modifier_necessity(self, note, sharp_flag):

        necessity = False

        if (note < 50):
            if(self.score.sharp == True):
                if (note % 12 == 0):
                    if (self.B_sharp == True and sharp_flag == False):
                        necessity = True
                        self.B_sharp = False
                    elif (self.B_sharp == False and sharp_flag == True):
                        necessity = True
                        self.B_sharp = True

                elif (note % 12 == 1 or note % 12 == 2):
                    if (self.C_sharp == True and sharp_flag == False):
                        necessity = True
                        self.C_sharp = False
                    elif (self.C_sharp == False and sharp_flag == True):
                        necessity = True
                        self.C_sharp = True

                elif (note % 12 == 3 or note % 12 == 4):
                    if (self.D_sharp == True and sharp_flag == False):
                        necessity = True
                        self.D_sharp = False
                    elif (self.D_sharp == False and sharp_flag == True):
                        necessity = True
                        self.D_sharp = True

                elif (note % 12 == 5):
                    if (self.E_sharp == True and sharp_flag == False):
                        necessity = True
                        self.E_sharp = False
                    elif (self.E_sharp == False and sharp_flag == True):
                        necessity = True
                        self.E_sharp = True

                elif (note % 12 == 6 or note % 12 == 7):
                    if (self.F_sharp == True and sharp_flag == False):
                        necessity = True
                        self.F_sharp = False
                    elif (self.F_sharp == False and sharp_flag == True):
                        necessity = True
                        self.F_sharp = True

                elif (note % 12 == 8 or note % 12 == 9):
                    if (self.G_sharp == True and sharp_flag == False):
                        necessity = True
                        self.G_sharp = False
                    elif (self.G_sharp == False and sharp_flag == True):
                        necessity = True
                        self.G_sharp = True

                elif (note % 12 == 10 or note % 12 == 11):
                    if (self.A_sharp == True and sharp_flag == False):
                        necessity = True
                        self.A_sharp = False
                    elif (self.A_sharp == False and sharp_flag == True):
                        necessity = True
                        self.A_sharp = True

            else:
                if (note % 12 == 11 or note % 12 == 0):
                    if (self.B_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.B_sharp = False
                    elif (self.B_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.B_sharp = -1

                elif (note % 12 == 1):
                    if (self.C_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.C_sharp = False
                    elif (self.C_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.C_sharp = -1

                elif (note % 12 == 2 or note % 12 == 3):
                    if (self.D_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.D_sharp = False
                    elif (self.D_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.D_sharp = -1

                elif (note % 12 == 4 or note % 12 == 5):
                    if (self.E_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.E_sharp = False
                    elif (self.E_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.E_sharp = -1

                elif (note % 12 == 6):
                    if (self.F_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.F_sharp = False
                    elif (self.F_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.F_sharp = -1

                elif (note % 12 == 7 or note % 12 == 8):
                    if (self.G_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.G_sharp = False
                    elif (self.G_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.G_sharp = -1

                elif (note % 12 == 9 or note % 12 == 10):
                    if (self.A_sharp == -1 and sharp_flag == False):
                        necessity = True
                        self.A_sharp = False
                    elif (self.A_sharp == False and sharp_flag == -1):
                        necessity = True
                        self.A_sharp = -1

        return necessity

    #Checks the necessity of connecting notes. If the connexion is upward, it returns r = 1; if its downward, r = -1 and if it isn't connected, r = 0. Returns the parameters of the connecting bar as well
    def connect_if_necessary(self, n, m, next_line):

        r = 0
        a = 0
        x = 0
        y = 0

        if(n.duration < 0.24 and n.connected == False and n.note[0] < 50):

            pre_note_shift = m * n.duration * 8
            connection_duration = 0
            offset, non_used = self.get_shifts_treble(n,0)
            total_vertical_shift = 0
            compass_cnt = self.durations_count
            up_note_con = 0
            down_note_con = 0
            max_shift = offset
            min_shift = offset
            y_start = self.pixel_offsetY
            y_limit = y_start

            while(n.nref.duration < 0.25 and n.nref.note[0] < 50 and compass_cnt < self.score.compass1/self.score.compass2):

                n.connected = True
                connection_duration = connection_duration + n.duration
                v_shift, non_used = self.get_shifts_treble(n.nref,0)
                total_vertical_shift = total_vertical_shift + v_shift - offset
                compass_cnt = compass_cnt + n.nref.duration

                y_limit = y_limit + 8 * m * (n.duration + n.nref.duration)

                if(n.note[0] > 26 and n.note[0] < 49):
                    up_note_con = up_note_con + 1

                elif(n.note[0] < 27):
                    down_note_con = down_note_con + 1

                if(v_shift > max_shift):
                    max_shift = v_shift

                if(v_shift < min_shift):
                    min_shift = v_shift

                n = n.nref

            if(connection_duration > 0):

                n.connected = True

                connection_duration = connection_duration + n.duration

                rng = math.floor(y_limit - y_start)

                #Draws the connecting bar and gets its parameters
                r, a, x, y = self.draw_connecting_line(connection_duration, total_vertical_shift, up_note_con, down_note_con, max_shift, min_shift, m, pre_note_shift, next_line, rng)

        #Returns: direction of connection, slope of the bar, starting coordinates of the bar
        return r, a, x, y

    def draw_connecting_line(self, d, tot_shift, up_ct, down_ct, max_shift, min_shift, m, pre_note_shift, next_line, rng):

        #Defines the slope of the bar (numbers defined almost empirically)

        a = tot_shift/((3.5 * m * d * 9) * (up_ct + down_ct))

        #Defines if it will be connected upward or downward, and defines the x and y offsets for the drawing of the connecting bar
        if(up_ct <= down_ct):
            start_shift_y = 17 #-9 + int(pre_note_shift)
            start_shift_x = -58 + min_shift
            r = 1

        else:
            start_shift_y = 0 #-27 + int(pre_note_shift)
            start_shift_x = 50 + max_shift
            r = -1

        if(next_line == True):
            return_shift_y = 150 + 15 * self.score.KS + start_shift_y
            return_shift_x = self.starting_offsetX + line_jump + start_shift_x

        else:
            return_shift_y = self.pixel_offsetY + start_shift_y
            return_shift_x = self.pixel_offsetX + start_shift_x

        #Draws the bar
        for j in range (rng + 2):
            for i in range (8):
                self.img_sheet[return_shift_x + math.floor(a*j) - i][return_shift_y + j] = [0,0,0]

        #Returns the direction of the connection, slope, position in the image
        return r, a, return_shift_x, return_shift_y

    #Checks the need of lower duration connections
    def check_more_connections(self, shift_x, shift_y, a, n, r, m):

        aux_duration = 0.125
        d = 1
        x = shift_x
        y = shift_y

        #At this point, the first notes duration has already been taken into account. Discount its value
        compass_cnt = self.durations_count - n.duration
        
        bar_count = 0
        note_count = 0


        while (n.nref.connected == True and compass_cnt < self.score.compass1/self.score.compass2):

            note_count = note_count + 1

            rng = 16 * m * n.duration

            while (aux_duration/d > n.duration):

                bar_count = bar_count + 1
                if(r == 1):
                    x = x + 12
                else:
                    x = x - 12

                #Draws the necessary extra connections
                self.draw_more_connections(a, x, y, n, m, rng, False)

                d = 2*d

            if(r == 1):
                x = x - 12*bar_count + a*rng

            else:
                x = x + 12*bar_count + a*rng
                

            y = y + rng/2 + 8 * m * n.nref.duration
            compass_cnt = compass_cnt + n.duration
            bar_count = 0
            d = 1
            n = n.nref

        if(n.duration < n.pref.duration):

            aux_duration = n.duration
            limit_duration = n.pref.duration

            rng = 8 * m * n.duration

            while (aux_duration * d < limit_duration):

                if(r == 1):
                    x = x + 12
                else:
                    x = x - 16
                
                #Draws the connections for the last note in the set
                self.draw_more_connections(a, x, y, n, m, rng, True)

                d = 2*d


    #Draws the necessary extra connections with the same slope as the primary connecting bar
    def draw_more_connections(self, a, x, y, n, m, rng, lastNote):

        x = math.floor(x)
        y = math.floor(y)

        for j in range (int(rng)):
            for i in range (8):
                if(lastNote == False):
                    self.img_sheet[x + math.floor(a*j) - i][y + j] = [0, 0, 0]
                else:
                    self.img_sheet[x - math.floor(a*j) - i][y - j] = [0, 0, 0]

    #Draws the complementary lines
    def draw_complementary_lines(self, shift):

        if(shift <= -81):
            
            rng = math.floor(((-1)*shift - 81)/18 + 1)

            for i in range (rng):
                for j in range (40): #size of complementary bar in pixels
                    self.img_sheet[self.pixel_offsetX - 90 - i*18][self.pixel_offsetY - 10 + j] = [0, 0, 0]

        elif(shift >= 27):

            rng = math.floor((shift - 27)/18 + 1)

            for i in range (rng):
                for j in range (40): #size of complementary bar in pixels
                    self.img_sheet[self.pixel_offsetX + 18 + i*18][self.pixel_offsetY - 10 + j] = [0, 0, 0]

    def draw_note_stem(self, x, y, a, n, r, min_shift, c):

        limit_x = x

        shift, non_used = self.get_shifts_treble(n, c)

        start_x = self.pixel_offsetX + shift - 8

        if (r == 1):
            start_y = self.pixel_offsetY + 17

        else:
            start_y = self.pixel_offsetY

        #At this point, the first notes duration has already been taken into account. Discount its value
        compass_cnt = self.durations_count - n.duration

        while (n.nref.connected == True and compass_cnt < self.score.compass1/self.score.compass2):

            rng = math.floor(limit_x - start_x)

            if (rng < 0):
                rng = rng * (-1)

            for i in range (rng):
                for j in range (2):
                    if (r == 1):
                        self.img_sheet[start_x - i][start_y + j] = [0, 0, 0]
                    else:
                        self.img_sheet[start_x + i][start_y + j] = [0, 0, 0]

            shift, non_used = self.get_shifts_treble(n.nref, c)
            start_x = math.floor(self.pixel_offsetX + shift - 8)
            start_y = math.floor(start_y + 8 * min_shift * (n.duration + n.nref.duration))
            limit_x = limit_x + a * 8 * min_shift * (n.duration + n.nref.duration)
            compass_cnt = compass_cnt + n.duration
            n = n.nref

        if(n.connected == True and compass_cnt < self.score.compass1/self.score.compass2):
            
            rng = math.floor(limit_x - start_x)

            if (rng < 0):
                rng = rng * (-1)

            for i in range (rng):
                for j in range (2):
                    if (r == 1):
                        self.img_sheet[start_x - i][start_y + j] = [0, 0, 0]
                    else:
                        self.img_sheet[start_x + i][start_y + j] = [0, 0, 0]

        
        

#TEST
Score1 = Score(5, 4, 4, 0, False)


Score1.insert_note(22, 0.25)
Score1.insert_note(52, 0.25)
Score1.insert_note(27, 0.0625)
Score1.insert_note(29, 0.0625)
Score1.insert_note(53, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(23, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(23, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(23, 0.125)
Score1.insert_note(30, 0.125)
Score1.insert_note(20, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(20, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(20, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(29, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(25, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(22, 0.125)
Score1.insert_note(27, 0.125)
Score1.insert_note(27, 1)



Score1.insert_note(34, 0.0625)
Score1.insert_note(7, 0.0625)
Score1.insert_note(18, 0.125)
Score1.insert_note(53, 0.125)
Score1.insert_note(20, 0.25)
Score1.insert_note(28, 0.125)
Score1.insert_note(52, 0.25)
Score1.insert_note(29, 0.125)
Score1.insert_note(26, 0.125)
Score1.insert_note(20, 0.5)
Score1.insert_note(27, 0.25)
Score1.insert_note(51, 0.5)
Score1.insert_note(27, 0.25)
Score1.insert_note(28, 0.125)
Score1.insert_note(28, 0.125)
Score1.insert_note(28, 0.125)
Score1.insert_note(28, 0.125)
Score1.insert_note(28, 0.125)
Score1.insert_note(14, 0.125)
Score1.insert_note(20, 0.25)
Score1.insert_note(28, 0.25)
Score1.insert_note(28, 0.25)
Score1.insert_note(28, 0.25)
Score1.insert_note(28, 0.25)
Score1.insert_note(29, 0.125)
Score1.insert_note(32, 0.125)
Score1.insert_note(50, 1)
Score1.insert_note(20, 0.25)
Score1.insert_note(16, 0.125)
Score1.insert_note(13, 0.25)
Score1.insert_note(28, 0.25)




image = Create_Image(Score1)
image.setup_clef_TS()
image.sweep_score()
cv2.imshow("lala", image.img_sheet)
cv2.imwrite('score.jpg', image.img_sheet)
cv2.waitKey()
#Score1.insert_note(4, 2, 1)
