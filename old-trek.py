# -*- coding: utf-8 -*-
import random


#*********************  GALAXY  **************************#

class Quadrant(object):
    __slots__ = (
          "bases"        # number of bases in this quadrant
        , "klingons"     # number of Klingons in this quadrant
        , "holes"        # number of black holes in this quadrant
        , "scanned"      # star chart entry (see below)
        , "stars"        # number of stars in this quadrant
        , "qsystemname"  # starsystem name (see below)
    )
    def __init__(self):
        self.bases = []
        self.klingons = []
        self.holes = []
        self.stars = []
        self.scanned = 0



class Galaxy(object):
    """
    Representation of galaxy
    """
    def __init__(self, nsects=10, nquads=8, ninhab=32):
        """
        @nsects -- dimensions of quadrant in sectors
        @nquads -- dimension of galaxy in quadrants
        @ninhab -- number of quadrants which are inhabited
        """






Q_DISTRESSED = 0200
Q_SYSTEM = 077

# systemname conventions:
# 1 -> NINHAB index into Systemname table for live system.
# + Q_DISTRESSED  distressed starsystem -- systemname & Q_SYSTEM
#         is the index into the Event table which will
#         have the system name
# 0       dead or nonexistent starsystem
#
# starchart ("scanned") conventions:
# 0 -> 999    taken as is
# -1      not yet scanned ("...")
# 1000        supernova ("///")
# 1001        starbase + ??? (".1.")

# ascii names of systems
systemnames = ["" for i in xrange(NINHAB)]
# quadrant definition (list of lists)
quads = [[Quadrant() for x in xrange(NQUADS)] for y in xrange(NQUADS)]

# defines for sector map  (below)
EMPTY      = '.'
STAR       = '*'
BASE       = '#'
ENTERPRISE = 'E'
QUEENE     = 'Q'
KLINGON    = 'K'
INHABIT    = '@'
HOLE       = ' '

# current sector map (list of lists)
sector = [['' for x in xrange(NSECTS)] for y in xrange(NSECTS)]


#************************ DEVICES ******************************#

NDEV     = 14  # max number of devices

# device tokens
WARP     = 0   # warp engines
SRSCAN   = 1   # short range scanners
LRSCAN   = 2   # long range scanners
PHASER   = 3   # phaser control
TORPED   = 4   # photon torpedo control
IMPULSE  = 5   # impulse engines
SHIELD   = 6   # shield control
COMPUTER = 7   # on board computer
SSRADIO  = 8   # subspace radio
LIFESUP  = 9   # life support systems
SINS     = 10  # Space Inertial Navigation System
CLOAK    = 11  # cloaking device
XPORTER  = 12  # transporter
SHUTTLE  = 13  # shuttlecraft

# devise names
class Device(object):
    __slots__ = (
          "name"    # device name
        , "person"  # the person who fixes it
    )

devices = [Device() for i in xrange(NDEV)]


#***************************  EVENTS  ****************************#

NEVENTS  = 12    # number of different event types

E_LRTB   = 1     # long range tractor beam
E_KATSB  = 2     # Klingon attacks starbase
E_KDESB  = 3     # Klingon destroys starbase
E_ISSUE  = 4     # distress call is issued
E_ENSLV  = 5     # Klingons enslave a quadrant
E_REPRO  = 6     # a Klingon is reproduced
E_FIXDV  = 7     # fix a device
E_ATTACK = 8     # Klingon attack during rest period
E_SNAP   = 9     # take a snapshot for time warp
E_SNOVA  = 10    # supernova occurs

E_GHOST  = 0100  # ghost of a distress call if ssradio out
E_HIDDEN = 0200  # event that is unreportable because ssradio out
E_EVENT  = 077   # mask to get event code

class Event(object):
    __slots__ = (
          "x", "y"      # coordinates
        , "date"        # trap stardate
        , "evcode"      # event type
        , "systemname"  # starsystem name
    )

# systemname conventions:
#  1 -> NINHAB index into Systemname table for reported distress calls
#
# evcode conventions:
#  1 -> NEVENTS-1  event type
#  + E_HIDDEN  unreported (SSradio out)
#  + E_GHOST   actually already expired
#  0       unallocated

MAXEVENTS = 25  # max number of concurrently pending events

events = [Event() for i in xrange(MAXEVENTS)]


#*****************************  KLINGONS  *******************************#

class Klingon(object):
    __slots__ = (
          "x", "y"    # coordinates
        , "power"     # power left
        , "distance"  # distance to Enterprise
        , "avgdist"   # average over this move
        , "srndreq"   # set if surrender has been requested
    )

MAXKLQUAD = 9  # maximum klingons per quadrant


#********************** MISCELLANEOUS ***************************#

# condition codes
GREEN  = 0
DOCKED = 1
YELLOW = 2
RED    = 3

# starbase coordinates
MAXBASES = 9  # maximum number of starbases in galaxy

# distress calls
MAXDISTR = 5  # maximum concurrent distress calls

# phaser banks
NBANKS   = 6  # number of phaser banks

class Point(object):
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

# note that much of the stuff in the following structs CAN NOT
# be moved around!!!!



# game related information, mostly scoring
class Game():
    killed_klingons = 0    # number of klingons killed
    killed_bases = 0       # number of starbases killed
    killed_stars = 0       # number of stars killed
    killed_inhabited = 0   # number of inhabited starsystems killed
    deaths = 0      # number of deaths onboard Enterprise
    negenbar = 0    # number of hits on negative energy barrier
    skill = 0       # skill rating of player
    length = 0      # length of game
    killed = False  # set if you were killed
    tourn = False   # set if a tournament game
    password = ""   # game password
    snap = False    # set if snapshot taken
    helps = 0       # number of help calls
    captives = 0    # total number of captives taken
