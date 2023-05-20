import math


class NACAModified:
    NP = 0

    XCC = []
    XU = []
    YU = []
    XL = []
    YL = []
    YT = []
    YC = []

    YLED = []

    DYC = []
    XQ = [0.0, 0.0]
    YQ = [0.0, 0.0]
    ALP = [0.0] * 14

    def __init__(self, num_points: int = 100):
        self.NP = num_points
        self.XCC = [0.0] * self.NP
        self.XU = [0.0] * self.NP
        self.YU = [0.0] * self.NP
        self.XL = [0.0] * self.NP
        self.YL = [0.0] * self.NP
        self.YT = [0.0] * self.NP
        self.YC = [0.0] * self.NP
        self.DYC = [0.0] * self.NP

        self.YLED = [0.0] * self.NP

    def calc_theta(self, SVAL) -> float:
        if SVAL == 0:
            return 0
        if SVAL == 1:
            return math.pi / 2
        if SVAL == -1:
            return -math.pi / 2
        return math.atan(SVAL / math.sqrt(1 - math.pow(SVAL, 2)))

    def set_coord_spacing(self, spacing: int):
        match spacing:
            case 1:
                DELTH = 1 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = DELTH * (I)
            case 2:
                DELTH = math.pi / 2 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = 1 - math.cos(DELTH * (I))
            case 3:
                DELTH = math.pi / 2 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = math.cos(math.pi / 2 - DELTH * (I))
            case _:
                # default to Full Cosine
                DELTH = math.pi / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = .5 - .5 * math.cos(DELTH * (I))

    def naca_four_modified(self, MM: int, PP: int, TOC: int, IP: int, TT: int, LED: float, LEDD: int):
        MC = MM / 100
        PC = PP / 10
        TC = TOC / 100
        TP = TT / 10
        D1 = (2.24 - 5.42 * TP + 12.3 * math.pow(TP, 2)) / 10 / (1 - .878 * TP)
        D2 = (.294 - 2 * (1 - TP) * D1) / math.pow(1 - TP, 2)
        D3 = (-.196 + (1 - TP) * D1) / math.pow(1 - TP, 3)
        A0 = .296904 * IP / 6
        R1 = math.pow(1 - TP, 2) / 5 / (.588 - 2 * D1 * (1 - TP))
        AA1 = .3 / TP - 15 * A0 / 8 / math.sqrt(TP) - TP / 10 / R1
        A2 = -.3 / math.pow(TP, 2) + 5 * A0 / 4 / math.pow(TP, 1.5) + 1 / 5 / R1
        A3 = .1 / math.pow(TP, 3) - .375 * A0 / math.pow(TP, 2.5) - 1 / 10 / R1 / TP

        for I in range(self.NP):
            if self.XCC[I] > TP:
                self.YT[I] = 5 * TC * (.002 + D1 * (1 - self.XCC[I]) + D2 * math.pow(1 - self.XCC[I], 2) + D3 * math.pow(1 - self.XCC[I], 3))
            else:
                self.YT[I] = 5 * TC * (A0 * math.sqrt(self.XCC[I]) + AA1 * self.XCC[I] + A2 * math.pow(self.XCC[I], 2) + A3 * math.pow(self.XCC[I], 3))

            if MM == 0: continue

            if self.XCC[I] > PC:
                self.YC[I] = MC / math.pow(1 - PC, 2) * (1 - 2 * PC + 2 * PC * self.XCC[I] - math.pow(self.XCC[I], 2))
                self.DYC[I] = 2 * MC / math.pow(1 - PC, 2) * (PC - self.XCC[I])
            else:
                self.YC[I] = MC / math.pow(PC, 2) * (2 * PC * self.XCC[I] - math.pow(self.XCC[I], 2))
                self.DYC[I] = 2 * MC / math.pow(PC, 2) * (PC - self.XCC[I])

        if LED > 0 and LEDD > 0:
            for I in range(self.NP):
                # do we have any droop to add to camber
                if self.XCC[I] < LEDD / 10:
                    self.YLED[I] = LED * math.pow(1 - (self.XCC[I] / (LEDD / 10)), 2)

        self.LER = 1.1019 * math.pow(IP / 6 * TC, 2)
        if IP >= 9:
            LER = 3 * 1.1019 * math.pow(TC, 2)

        self.TEANG = 2 * math.atan(1.16925 * TC)

        DESIG = MM * 1000 + PP * 100 + TOC
        SESIG = IP * 10 + TT
        self.DESIG_str = "{:04d}".format(DESIG) + "-" + "{:02d}".format(SESIG)

        # now derive the surfaces
        for I in range(self.NP):
            THET = 0  # math.atan(DYC[I])
            self.XU[I] = self.XCC[I] - self.YT[I] * math.sin(THET)
            self.YU[I] = self.YC[I] + self.YT[I] * math.cos(THET) - self.YLED[I]
            self.XL[I] = self.XCC[I] + self.YT[I] * math.sin(THET)
            self.YL[I] = self.YC[I] - self.YT[I] * math.cos(THET) - self.YLED[I]

    def naca_five_modified(self, LL: int, PP: int, QQ: int, TOC: int, IP: int, TT: int, LED: float, LEDD: int):
        if QQ < 0 or QQ > 1:
            raise Exception("third digit should be 0 (normal) or 1 (reflex) for camber line")

        LC = LL / 10
        PC = PP / 20
        TC = TOC / 100
        MC = PC / 2
        TP = TT / 10
        D1 = (2.24 - 5.42 * TP + 12.3 * math.pow(TP, 2)) / 10 / (1 - .878 * TP)
        D2 = (.294 - 2 * (1 - TP) * D1) / math.pow((1 - TP), 2)
        D3 = (-.196 + (1 - TP) * D1) / math.pow((1 - TP), 3)
        A0 = .296904 * IP / 6
        R1 = math.pow((1 - TP), 2) / 5 / (.588 - 2 * D1 * (1 - TP))
        AA1 = .3 / TP - 15 * A0 / 8 / math.sqrt(TP) - TP / 10 / R1
        A2 = -.3 / math.pow(TP, 2) + 5 * A0 / 4 / math.pow(TP, (1.5)) + 1 / 5 / R1
        A3 = .1 / math.pow(TP, 3) - .375 * A0 / math.pow(TP, (2.5)) - 1 / 10 / R1 / TP

        while (True):
            PCT = math.sqrt(math.pow(MC, 2) * (MC / 3 - 2 * math.sqrt(MC / 3) + 1))
            if abs(PC - PCT) <= .0001:
                break

            MC = MC * PC / PCT

        SVAL = 1 - 2 * MC

        THETA = self.calc_theta(SVAL)

        QC = (3 * MC - 7 * math.pow(MC, 2) + 8 * math.pow(MC, 3) - 4 * math.pow(MC, 4)) / math.sqrt(MC * (1 - MC)) - 1.5 * (1 - 2 * MC) * (math.pi / 2 - THETA)
        K1 = 9 * LC / QC
        K2K1 = (3 * math.pow((MC - PC), 2) - math.pow(MC, 3)) / math.pow((1 - MC), 3)

        for I in range(self.NP):
            # thickness distribution (before/after max thickness position)
            if self.XCC[I] > TP:
                self.YT[I] = 5 * TC * (.002 + D1 * (1 - self.XCC[I]) + D2 * math.pow((1 - self.XCC[I]), 2) + D3 * math.pow((1 - self.XCC[I]), 3))
            else:
                self.YT[I] = 5 * TC * (A0 * math.sqrt(self.XCC[I]) + AA1 * self.XCC[I] + A2 * math.pow(self.XCC[I], 2) + A3 * math.pow(self.XCC[I], 3))

            if LL == 0: continue  # LL is lift, 0 implies no lift, eg tail fin or strake

            # camber distribution
            if QQ == 0:  # normal camber curve
                if self.XCC[I] > MC:  # Back
                    self.YC[I] = (K1 / 6) * math.pow(MC, 3) * (1 - self.XCC[I])
                    self.DYC[I] = (-K1 / 6) * math.pow(MC, 3)
                else:  # Front
                    self.YC[I] = (K1 / 6) * (math.pow(self.XCC[I], 3) - 3 * MC * math.pow(self.XCC[I], 2) + math.pow(MC, 2) * (3 - MC) * self.XCC[I])
                    self.DYC[I] = (K1 / 6) * (3 * math.pow(self.XCC[I], 2) - 6 * MC * self.XCC[I] + math.pow(MC, 2) * (3 - MC))
            else:  # reflex camber curve
                if self.XCC[I] > MC:  # Back
                    self.YC[I] = (K1 / 6) * (
                            K2K1 * math.pow((self.XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * self.XCC[I] - math.pow(MC, 3) * self.XCC[I] + math.pow(
                        MC, 3))
                    self.DYC[I] = (K1 / 6) * (3 * K2K1 * math.pow((self.XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))
                else:  # Front
                    self.YC[I] = (K1 / 6) * (
                            math.pow((self.XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * self.XCC[I] - math.pow(MC, 3) * self.XCC[I] + math.pow(MC, 3))
                    self.DYC[I] = (K1 / 6) * (3 * math.pow((self.XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))

        if LED > 0 and LEDD > 0:
            for I in range(self.NP):
                # do we have any droop to add to camber
                if self.XCC[I] < LEDD / 10:
                    self.YLED[I] = LED * math.pow(1 - (self.XCC[I] / (LEDD / 10)), 2)

        # leading edge radius
        self.LER = 1.1019 * math.pow((IP / 6 * TC), 2)

        if IP >= 9:
            self.LER = 3 * 1.1019 * math.pow((TC), 2)

        # trailing edge angle
        self.TEANG = 2 * math.atan(1.16925 * TC)

        # designation
        DESIG = LL * 10000 + PP * 1000 + QQ * 100 + TOC

        # modification designation
        SESIG = IP * 10 + TT
        self.DESIG_str = "{:05d}".format(DESIG) + "-" + "{:02d}".format(SESIG)

        # now derive the surfaces
        for I in range(self.NP):
            THET = 0  # math.atan(DYC[I])
            self.XU[I] = self.XCC[I] - self.YT[I] * math.sin(THET)
            self.YU[I] = self.YC[I] + self.YT[I] * math.cos(THET) - self.YLED[I]
            self.XL[I] = self.XCC[I] + self.YT[I] * math.sin(THET)
            self.YL[I] = self.YC[I] - self.YT[I] * math.cos(THET) - self.YLED[I]

    def get_profile_verts_and_edges(self, chord_length: float) -> list[list[list[float]], list[list[int]]]:
        # verts are in x/z plane with 0 y
        verts = []  # list of lists of 3 floats [x,y,z]
        edges = []  # list of lists of 2 vertex indices [1,2]

        for I in range(self.NP - 1, -1, -1):
            verts.append([self.XU[I] * chord_length, 0, self.YU[I] * chord_length])

        # then forward along the lower
        for I in range(self.NP):
            verts.append([self.XL[I] * chord_length, 0, self.YL[I] * chord_length])

        for I in range((self.NP * 2) - 1):
            edges.append([I, I + 1])

        # finally close the path at the trailing edge
        if self.YU[self.NP - 1] != self.YL[self.NP - 1]:
            edges.append([(self.NP * 2) - 1, 0])

        return [verts, edges]
