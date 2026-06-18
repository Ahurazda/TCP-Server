import socket
import re

import numpy as np

# TODO: Float coordinates
def getVal(conn, max, s):

  var = ''
  j = 0
  while (True):

      if j >= (max-1):
          return -1, var

      conn.settimeout(TIMEOUT)

      try:
          sec = conn.recv(BUFFER_SIZE)
      except socket.timeout:

          return 1,var

      sec = sec.decode('UTF-8')
      print(sec)
      if sec == '\a':
        conn.settimeout(TIMEOUT)
        try:
            dec = conn.recv(BUFFER_SIZE).decode('UTF-8')

        except socket.timeout:
            return 1, var

        if dec == '\b':
            return 0, var
        var += sec
        var += dec
        j += 1

      else:
        var += sec
        j += 1


def nametoHash(name):

    val = 0
    for i in name:
        val += ord(i)
    val = (val * 1000) % 65536
    return val

def toHash( name , keyID):
    val = 0
    for i in name:
        val += ord(i)
    val = (val * 1000) % 65536
    val = (val + serverKey(keyID)) % 65536

    return val


def serverKey( keyID ):

    serverKeys = [23019,32037,18789,16443,18189]
    return serverKeys[keyID]


def clientKey( keyID ):

   clientKeys = [32037, 29295, 13603, 29533,21952]
   return clientKeys[keyID]


def getHash( confCode , keyID, name ):

    x = 0
    hash = nametoHash(name)
    if ( ( hash+clientKey(keyID) ) > 65535 ):
      x = (65536 + confCode) - clientKey(keyID)
    else:
      x = confCode - clientKey(keyID)
    if hash == x:
        return 1
    else:
        return 0

def finalize( conn ):
    conn.sendall(bytes('105 GET MESSAGE' + str(a) + str(b), 'UTF-8'))

    ret, finalMessage = getVal(conn, 100, s)

    if ret != 0:
        if ret == -1:
            conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
        return

    conn.sendall(bytes('106 LOGOUT' + str(a) + str(b), 'UTF-8'))



def idDirection( precoordinates, coordinates ):        # identificate which direction are you on

    if (precoordinates[0] == coordinates[0]):          # up/down

        if (coordinates[1] > precoordinates[1]):
            direction = 1
        else:
            direction = 3
    else:                                               # right/left
        if (coordinates[0] > precoordinates[0]):
            direction = 2
        else:
            direction = 4

    return direction


def difference(dir1, dir2):

    if dir1 > dir2:
        return dir1-dir2
    elif dir1 < dir2:
        return dir2-dir1


def chooseDir(coordinates):                 # choose direction robot should go

      if coordinates[0] == 0:
        if coordinates[1] > 0:
            return 3
        else:
            return 1
      elif coordinates[1] == 0:  # on x axes
          if coordinates[0] > 0:
              return 4
          else:
              return 2

      elif abs(coordinates[0]) > abs(coordinates[1]):  # go to x axes

        if (coordinates[1] > 0  and coordinates[0] > 0):  # down
            return 3
        elif ( coordinates[1] < 0 and  coordinates[0] < 0 ):  #up
            return 1
        elif (coordinates[1] < 0 and coordinates[0] > 0):     # up
            return 1
        elif  coordinates[1] > 0 and coordinates[0] < 0 :     #down
            return 3
      else:
        if (coordinates[1] > 0 and coordinates[0] > 0):               #// jdi doleva
            return 4
        elif ( coordinates[1] < 0 and  coordinates[0] < 0 ):                   # // jdi doprava
            return 2
        elif (coordinates[1] < 0 and coordinates[0] > 0):             # doleva
            return 4
        elif ( coordinates[1] > 0 and coordinates[0] < 0 ):           #doprava
            return 2


def turn(conn, direction, rightdir, s):

    if direction == 1 and rightdir == 4:

        conn.sendall(bytes('103 TURN LEFT' + str(a) + str(b), 'UTF-8'))
        ret, coordB = getVal(conn, 12, s)
        if ret != 0 or not 'OK' in coordB:
            if ret == -1:
              return -1
        coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')

        if len(coordinates) != 2:
            return -1

    elif direction == 4 and rightdir == 1:
        conn.sendall(bytes('104 TURN RIGHT' + str(a) + str(b), 'UTF-8'))
        ret, coordB = getVal(conn, 12, s)
        if ret != 0 or not 'OK' in coordB:
            if ret == -1:
                return -1
        coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')

        if len(coordinates) != 2:
            return -1
    elif direction > rightdir:
        for i in range(difference(direction, rightdir)):
            conn.sendall(bytes('103 TURN LEFT' + str(a) + str(b), 'UTF-8'))
            ret, coordB = getVal(conn, 12, s)
            if ret != 0 or not 'OK' in coordB:
                if ret == -1:
                    return -1
            coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')

            if len(coordinates) != 2:
                return -1
    elif direction < rightdir:
        for i in range(difference(direction, rightdir)):
            conn.sendall(bytes('104 TURN RIGHT' + str(a) + str(b), 'UTF-8'))
            ret, coordB = getVal(conn, 12, s)
            if ret != 0 or not 'OK' in coordB:
                if ret == -1:
                    return -1
            coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')

            if len(coordinates) != 2:
                return -1

TIMEOUT = 1.0                                                       # global variable
BUFFER_SIZE = 1

if __name__ == '__main__':

  HOST = ''  # Standard loopback interface address (localhost)
  PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
  a = '\a'
  b = '\b'

  while (True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))        # assigning interface and port  to socket
        s.listen()                  # accept connections
        conn, addr = s.accept()     # blocks, then returns new socket
        with conn:
            while True:
                # ------------ ----------------------------------------- AUTHENTIZATION
                conn.setblocking(True)
                ret, name = getVal(conn, 20, s)
                if ret != 0:
                    if ret == -1:
                      conn.sendall(bytes('301 SYNTAX ERROR' + str('\a') + str('\b'), 'UTF-8'))
                    break

                conn.sendall(bytes('107 KEY REQUEST' + str(a) + str(b), 'UTF-8'))


                ret, keyID = getVal(conn, 5, s)
                if ret != 0 or not keyID.isdigit():

                        # originally if condition doing command under based on it's
                        conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                        break

                keyID = int(keyID)
                if keyID > 4 or keyID < 0:
                 conn.sendall(bytes('303 KEY OUT OF RANGE' + str(a) + str(b), 'UTF-8'))
                 break

                conn.sendall(bytes(str((toHash(name, keyID))) + str(a) + str(b), 'UTF-8'))
                ret, confCode = getVal(conn, 7, s)



                if ret != 0 or not confCode.isdigit() or ' ' in confCode:
                    if ret != 1:
                      conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                    break

                confCode = int(confCode)
                if confCode < 0 or not getHash(confCode, keyID, name) :    #incorrect hash
                    print(nametoHash(name))
                    print( confCode)
                    conn.sendall(bytes('300 LOGIN FAILED' + str(a) + str(b), 'UTF-8'))
                    break

                conn.sendall(bytes('200 OK' + str(a) + str(b), 'UTF-8'))

                maxMoves = 0
                numHits = 0
                hitObstacle = False
                direction = 0
                finalMessage = ''
                # -----------------------------------------------------------------------------MOVEMENT

                conn.sendall(bytes('102 MOVE' + str(a) + str(b), 'UTF-8'))

                ret, coordB = getVal(conn, 12, s)
                if ret != 0 or not 'OK' in coordB or ' ' in coordB:
                    if ret != 1:
                      conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                    break

                coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                if len(coordinates) != 2:
                    conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                    break


                if coordinates[0] == 0 and coordinates[1] == 0:

                    finalize(conn)
                    break

                precoordinates = coordinates
                # ---------------------------------------------------------------------------------------
                conn.sendall(bytes('102 MOVE' + str(a) + str(b), 'UTF-8'))

                ret, coordB = getVal(conn, 12, s)
                if ret != 0 or not 'OK' in coordB:
                    if ret == -1:
                      conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                    break

                coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                if len(coordinates) != 2:
                    conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                    break

                if np.array_equal(coordinates, precoordinates):  # robot hit a obstacle
                    numHits += 1
                    hitObstacle = True
                else:  # robot did a move
                    maxMoves += 1

                if coordinates[0] == 0 and coordinates[1] == 0:
                    finalize(conn)
                    break


                runInside = False
                onAxes = False

                while True:                                                              # proceed making movements

                   if hitObstacle:

                       if coordinates[0] == 0 or coordinates[1] == 0:                   # if is on an axes
                           onAxes = True

                       conn.sendall(bytes('103 TURN LEFT' + str(a) +str(b), 'UTF-8'))
                       ret, coordB = getVal(conn, 12, s)
                       if ret != 0 or not 'OK' in coordB:
                           if ret == -1:
                               conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                           break
                       coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                       if len(coordinates) != 2:
                           conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                           break

                       conn.sendall(bytes('102 MOVE' + str(a) + str(b), 'UTF-8'))

                       ret, coordB = getVal(conn, 12, s)
                       if ret != 0 or not 'OK' in coordB:
                           if ret == -1:
                               conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                           break

                       precoordinates = coordinates
                       coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                       if len(coordinates) != 2:
                           conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                           break

                       if coordinates[0] == 0 and coordinates[1] == 0:
                           finalize(conn)
                           break

                       if onAxes:

                           conn.sendall(bytes('104 TURN RIGHT' + str(a) + str(b), 'UTF-8'))
                           ret, coordB = getVal(conn, 12, s)
                           if ret != 0 or not 'OK' in coordB:
                               if ret == -1:
                                   conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                               break
                           coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                           if len(coordinates) != 2:
                               conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                               break

                           conn.sendall(bytes('102 MOVE' + str(a) + str(b), 'UTF-8'))

                           ret, coordB = getVal(conn, 12, s)
                           if ret != 0 or not 'OK' in coordB:
                               if ret == -1:
                                   conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                               break

                           precoordinates = coordinates
                           coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')
                           if len(coordinates) != 2:
                               conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                               break
                           maxMoves += 1

                       maxMoves += 1
                       hitObstacle = False
                       onAxes = False

                   else:                                        # ROBOT DID NOT HIT OBSTACLE

                     direction = idDirection(precoordinates, coordinates)
                     rightdir = chooseDir(coordinates)
                     if turn(conn, direction, rightdir, s) == -1:
                        conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                        break
                     runInside = True
                     conn.sendall(bytes('102 MOVE' + str(a) + str(b), 'UTF-8'))

                     ret, coordB = getVal(conn, 12, s)
                     if ret != 0 or not 'OK' in coordB:
                         if ret == -1:
                             conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                         break

                     precoordinates = coordinates
                     coordinates = np.array([float(s) for s in re.findall(r'-?\d+\.?\d*', coordB)], dtype='int')

                     if len(coordinates) != 2:
                         conn.sendall(bytes('301 SYNTAX ERROR' + str(a) + str(b), 'UTF-8'))
                         break
                     if coordinates[0] == 0 and coordinates[1] == 0:
                         finalize(conn)
                         break

                     if np.array_equal(coordinates, precoordinates):  # robot hit a obstacle
                         numHits += 1
                         hitObstacle = True
                     else:  # robot did a move
                         maxMoves += 1

                break
