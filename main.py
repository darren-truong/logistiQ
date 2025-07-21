import csv # import csv for reading text from csv files
import math # import math to use ceiling function to add floats properly


class PackageHashTable:
    # default size is 40, create an outer list and have it store multiple inner lists in the table attribute
    def __init__(self, size=40):
        self.size = size
        self.table = []
        for i in range(size):
            self.table.append([])

    # hash function so that package ID 1 for example hashes to the 0th bucket/index of list by subtracting 1 from the ID then taking the remainder of that vlaue
    def _hash(self, packID):
        return (packID - 1) % self.size

    # to add a package, get the package ID from the package which will be used as a key for the hash table, then throw it into the hash function to get the bucket/index of which list to append the package to
    # my hash table is a self-adjusting data structure that utilizes chaining because even if the hash function maps 2 packages to the same bucket/index, the inner list simply grows as both packages get appended to the same inner list
    # this should fulfill part A because a package object contains all the information such as address, deadline, city, zipcode, weight, status, etc. as its attributes, and the entire package object is stored in the hash table
    def add(self, package):
        bucket = self._hash(package.packID)
        self.table[bucket].append(package)

    # to get a package, find the bucket it resides in by using the hash function, then traverse that list and return the package that has a package ID matching the package ID provided to the function
    # this should fulfill part B because it returns the package object, and the package attributes can then be accessed to get delivery address, deadline, city, zipcode, weight, status, etc.
    def get(self, packID):
        bucket = self._hash(packID)
        result = None
        for package in self.table[bucket]:
            if package.packID == packID:
                result = package
        return result

    # find a specific package by using the get method, then iterate through all the attributes in the package object and print it out for the user
    def printPackage(self, packID):
        package = self.get(packID)
        for key, value in package.__dict__.items():
            print(f"{key}: {value}", end=" | ")
        print()
        print()

    # iterate through all the buckets and for each bucket, print out every package in that bucket/inner list
    def printAll(self):
        for bucket in self.table:
            for package in bucket:
                for key, value in package.__dict__.items():
                    print(f"{key}: {value}", end=" | ")
                print()
        print()

class Package:
    def __init__(self, packID, address, addressIndex, city, state, zipcode, deadline, weight, status, deliveryTime):
        self.packID = packID # unique package ID 
        self.address = address # address the package is to be delivered to
        self.addressIndex = addressIndex # addressIndex to find the address in the addressTable
        self.city = city # city the package is to be delivered to
        self.state = state # state the package is to be delivered to
        self.zipcode = zipcode # zipcode the package is to be delivered to
        self.deadline = deadline # deadline the package is to be delivered by
        self.weight = weight # weight of the package
        self.status = status # delivery status (ex. at hub OR on route truck 1 OR delivered by truck 1)
        self.deliveryTime = deliveryTime # delivery time of the package which is either the time it was delivered or the string 'N/A'

class Truck:
    def __init__(self, truID, departureSeconds, userSeconds, packsID, packageTable):
        self.currentAddress = 0 # index to find the address in the addressTable and is where the truck is currently located
        self.maxPackages = 16 # maximum amount of packages a truck can hold at once
        self.mileage = 0 # how many miles the truck has traveled so far
        self.elapsedSeconds = 0 # how much time has passed from the truck's point of view (number goes from 0 to 32400 which corresponds to 8:00:00-17:00:00)
        self.recallTime = 'N/A' # what time the truck returned to the hub if available

        self.truID = truID # the id of the truck
        self.departureSeconds = departureSeconds # the time at which the truck starts delivering packages (number goes from 0 to 32400 which corresponds to 8:00:00-17:00:00)
        self.departureTime = convertSecondsToTime(departureSeconds) # the time at which the truck starts delivering packages in a time string format 'HH:MM:SS'
        self.userSeconds = userSeconds # the deadline in seconds at which the truck has to stop (number goes from 0 to 32400 which corresponds to 8:00:00-17:00:00) which allows the user to see how far the simulation has run up to a certain point in time

        self.cargo = list() 
        for packID in packsID: # pass in a list of package IDs for the truck, and for every ID number, find the corresponding package in the hash table and append it to the cargo list
            self.cargo.append(packageTable.get(packID))

        self.addresses = set()
        for package in self.cargo: # iterate over all the packages loaded onto the truck and use a set to keep track of which addresses the truck has to visit in order to prevent duplicate addresses from populating the data structure
            self.addresses.add(package.addressIndex)

    def deliver(self, distanceTable):
        self.elapsedSeconds = self.departureSeconds # doing this moves time forward for the truck so that it can leave at the earliest time it is allowed
        if self.elapsedSeconds < self.userSeconds: # if there is still time for the truck to perform actions then continue otherwise stop
            print(f"Truck {self.truID} departed at {self.departureTime}") # example: if truck can leave at 8:00:00 and user gives time 8:00:01 then at 8:00:01 the truck is traveling to the next (COMMENT CONTINUED DOWN BELOW)
            # location so the packages loaded onto it are in transit and the truck has left otherwise if truck can leave at 8:00:00 and user gives time 8:00:00 then all the packages on this truck are still in hub and the truck hasn't left yet
            print()
            for package in self.cargo: # iterate over every package on the truck and update its status to be en route if there is time to perform actions
                package.status = f"En Route (Truck {self.truID})"
        while self.elapsedSeconds < self.userSeconds and len(self.cargo) > 0: # while there is still time remaining to possibly go to the nearest location and the truck still has packages to deliver
            minDeliveryDistance = float('inf')
            minDeliveryIndex = float('inf')
            for possibleDeliveryIndex in self.addresses: # iterate over all the unvisited addresses the truck must go to in order to find the closest address possible to visit
                if distanceTable[self.currentAddress][possibleDeliveryIndex] is not None: # if a distance number exists for this index combination then set possibleDeliveryDistance to be this number to signify this is the distance to an address the truck can possibly visit
                    possibleDeliveryDistance = distanceTable[self.currentAddress][possibleDeliveryIndex]
                else: # otherwise if the distance number does not exist for these two index combination simply flip the numbers to get the distance since distance x to y is the same as distance y to x and the table only stores the value once
                    possibleDeliveryDistance = distanceTable[possibleDeliveryIndex][self.currentAddress]
                if possibleDeliveryDistance < minDeliveryDistance:  # if the proposed address is closer than the current lowest address recorded, visit this location instead
                    minDeliveryIndex = possibleDeliveryIndex
                    minDeliveryDistance = possibleDeliveryDistance
            if self.elapsedSeconds + math.ceil(minDeliveryDistance / 0.005) > self.userSeconds: # even though the closest address to visit was found above, do we even have enough time to visit it? if not, break out of the entire loop
                break
            self.mileage = round(self.mileage + minDeliveryDistance, 1) # we have now visited the new address, so add the distance traveeled to the truck's total mileage
            self.elapsedSeconds += math.ceil(minDeliveryDistance / 0.005) # add the time we have spent traveling to the new location in order to show that time has passed for the truck
            self.currentAddress = minDeliveryIndex # change the currentAddress property to represent the new location that we are now at
            for package in self.cargo[:]: # now that we are at the new location, its time to deliver the packages so loop over all the packages that the truck is carrying and deliver the ones that have a matching address to the current location of the truck
                if package.addressIndex == self.currentAddress:
                    package.status = f"Delivered (Truck {self.truID})" # when a package has been delivered, it's status needs to be altered to say delivered by which truck
                    package.deliveryTime = convertSecondsToTime( # record the time at which the package was delivered
                        self.elapsedSeconds)
                    self.cargo.remove(package) # remove the delivered package from the truck's cargo list
            self.addresses.remove(self.currentAddress) # remove the current address from the truck's list of unvisited addresses

    def recall(self, distanceTable):
        if len(self.cargo) == 0 and len(self.addresses) == 0: # only recall a truck if it actually finished all of its deliveries
            self.mileage = round( # add the distance the truck has traveled to return to the hub from its current location
                self.mileage + distanceTable[self.currentAddress][0], 1)
            self.elapsedSeconds += math.ceil( # add the time truck has taken to return back to the hub
                distanceTable[self.currentAddress][0] / 0.005)
            self.currentAddress = 0 # change the current address of the truck to be at the hub
            self.recallTime = convertSecondsToTime(self.elapsedSeconds) # note the time the truck returned to the hub as a time string in the format 'HH:MM:SS'
            print(f"Truck {self.truID} returned at {self.recallTime}")
            print()


def loadAddressData(): # load the address table with data read from the addressCSV file
    addressTable = list()
    with open('csv/addressCSV.csv', mode='r', encoding='utf-8-sig') as file:
        addressReader = csv.reader(file)
        for row in addressReader:
            addressTable.append(row[0])
    return addressTable


def loadDistanceData(addressTableLength): # load the distance table which is a two-dimensional list with data read from the distanceCSV file
    distanceTable = list()
    for i in range(addressTableLength):
        distanceTable.append([None] * addressTableLength)
    with open('csv/distanceCSV.csv', mode='r', encoding='utf-8-sig') as file:
        distanceReader = csv.reader(file)
        rowIndex = 0
        for row in distanceReader:
            columnIndex = 0
            for column in row:
                if column:
                    distanceTable[rowIndex][columnIndex] = float(column)
                columnIndex += 1
            rowIndex += 1
    return distanceTable


def loadPackageData(addressTable, userSeconds): # load the package hash table with data read from the packageCSV file
    packageTable = PackageHashTable()
    with open('csv/packageCSV.csv', mode='r', encoding='utf-8-sig') as file:
        packageReader = csv.reader(file)
        for row in packageReader:
            package = Package(int(row[0]), row[1], addressTable.index(
                row[1]), row[2], row[3], row[4], row[5], int(row[6]), 'At hub', 'N/A')
            # these specific packages are delayed on flight and will not arrive to the depot until 9:05AM
            # at 9:05:00 on the dot, the package is at the hub but not en route
            # after 9:05:00, such as at 9:05:01, the packages are immediately loaded onto Truck 2 and then considered en route towards their destination
            if package.packID in [6, 25, 28, 32] and userSeconds < 3900:
                package.status = 'Delayed on flight'
            packageTable.add(package)
    return packageTable

# this function converts a time string between 8:00:00 and 17:00:00 to seconds which is used by the program to keep track of time during deliveries and used for other calculations
# 8:00:00 turns into 0 seconds
# 17:00:00 turns into 32400 seconds
def convertTimeToSeconds(userTime):
    hours, minutes, seconds = map(int, userTime.split(':'))
    userSeconds = (hours - 8) * 3600 + minutes * 60 + seconds
    return userSeconds

# this function edits the address for a specific package identified by its package ID after it has been loaded on a specific truck
def editAddress(packID, truck, editAddress, editSeconds, userSeconds, packageTable):
    if userSeconds > editSeconds: # only make the edit to the address if the user asks for the status of packages after a certain time
        editPackage = packageTable.get(packID)

        oldAddressIndex = editPackage.addressIndex
        counter = 0
        for package in truck.cargo: # after the address has been edited, we need to remove the old address from the list of places the truck has to visit but only do so if the old address had only one package that needed to be delivered to that location
            if package.addressIndex == oldAddressIndex:
                counter += 1
        if counter == 1:
            truck.addresses.remove(oldAddressIndex)

        editPackage.address = editAddress[0]
        editPackage.addressIndex = editAddress[1]
        editPackage.city = editAddress[2]
        editPackage.state = editAddress[3]
        editPackage.zipcode = editAddress[4]
        truck.addresses.add(editAddress[1]) # add the new address of the edited package to the list of places the truck has to visit
        print(f"Package {packID}'s address has been successfully edited!")
        print()

# this function converts seconds which are used by the truck object to a time string between 8:00:00 and 17:00:00 for display to the user
# 0 seconds corresponds to 8:00:00
# 32400 seconds corresponds to 17:00:00
def convertSecondsToTime(elapsedSeconds):
    totalSeconds = elapsedSeconds + 8 * 3600
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = totalSeconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"

# function simulates delivery of packages by first getting address data, distance data, and package data from the csv files
# time is also kept track of in seconds, because the timeframe is 8:00:00-17:00:00, 8:00:00 corresponds to 0 seconds and 17:00:00 corresponds to 32400 seconds
# after data from csv files are loaded, the truck objects are created using hard coded cargo lists, which means the trucks are manually loaded
# each truck will then deliver all their packages and return to the hub
# before truck 3 departs, the address for package ID 9 will be altered if the time given by the user is past 10:20:00
# depending on the user options, information for a specific package or all packages will then be printed
def startDeliveryProgram(userPackID, userTime, showMileage):
    print("SIMULATION START")
    print()

    # get address data from csv file and load it into a list
    addressTable = loadAddressData()
    print("Address table loaded!")

    # get distance data from csv file and load it into a matrix (list of lists)
    distanceTable = loadDistanceData(len(addressTable))
    print("Distance table loaded!")

    # get distance data from csv file and load it into a custom hash table (list of lists)
    packageTable = loadPackageData(addressTable, convertTimeToSeconds(userTime))
    print("Package table loaded!")
    print()

    # convert the amount of seconds (0 seconds = 8:00:00 and 32400 seconds = 17:00:00) back to a time string in the format HH:MM:SS for later use for display
    userSeconds = convertTimeToSeconds(userTime)

    # since we have 40 package IDs, manually determine which package goes on which truck
    truckOneCargo = [1, 4, 5, 7, 13, 14, 15,
                     16, 19, 20, 29, 30, 31, 34, 37, 40]
    truckTwoCargo = [2, 3, 6, 10, 11, 12, 18,
                     25, 26, 27, 28, 32, 33, 35, 36, 38]
    truckThreeCargo = [8, 9, 17, 21, 22, 23, 24, 39]

    # create truck objects and pass in 0 seconds for truck 1 since it can leave immediately at 8:00:00, pass in 3900 seconds for truck 2 since it can't leave until 9:05:00, and pass in 8400 seconds for truck 3 since it can't leave until 10:20:00
    truckOne = Truck(1, 0, userSeconds, truckOneCargo, packageTable)
    truckTwo = Truck(2, 3900, userSeconds, truckTwoCargo, packageTable)
    truckThree = Truck(3, 8400, userSeconds, truckThreeCargo, packageTable)

    # truck 1 deliver and return to hub
    truckOne.deliver(distanceTable)
    truckOne.recall(distanceTable)

    # truck 2 deliver and return to hub
    truckTwo.deliver(distanceTable)
    truckTwo.recall(distanceTable)

    # before truck 3 departs, edit the address if possible
    editAddress(9, truckThree, ['410 S State St', addressTable.index('410 S State St'), 'Salt Lake City', 'UT', '84111'], convertTimeToSeconds('10:20:00'), userSeconds, packageTable)

    # truck 3 deliver and depart
    truckThree.deliver(distanceTable)
    truckThree.recall(distanceTable)

    # determine whether to print information regarding all packages or just one specific package
    if userPackID == -1:
        packageTable.printAll()
    else:
        packageTable.printPackage(userPackID)

    # if every package has been delivered, it means the simulation has been completed, and if showMileage is True, print out the mileage 
    if len(truckOne.cargo) == 0 and len(truckTwo.cargo) == 0 and len(truckThree.cargo) == 0 and showMileage:
        print(f"Truck 1 mileage: {truckOne.mileage} miles")
        print(f"Truck 2 mileage: {truckTwo.mileage} miles")
        print(f"Truck 3 mileage: {truckThree.mileage} miles")
        print(f"The total mileage is: {round(truckOne.mileage + truckTwo.mileage + truckThree.mileage, 1)}")
        print()


# main function provides menu options and waits for user input to execute the delivery program under specific conditions and will loop back on itself to allow for other options to be chosen until 4 is chosen to quit out of the program
def main():
    userOption = None
    while True:
        print("Welcome to the delivery program!")
        print("Please input a number between 1-4 corresponding to the options below and press the enter key")
        print("1) Get all packages and total mileage after full completion of simulation")
        print("2) Get all packages at a specified time between 8:00:00 and 17:00:00")
        print("3) Get a single package at a specified time between 8:00:00 and 17:00:00")
        print("4) Quit")
        print()
        userOption = input("YOUR INPUT: ").strip()
        if not userOption.isdigit():
            print("Invalid input, please enter a number")
            print()
            continue
        userOption = int(userOption)
        if userOption == 1: # if option 1 is chosen, run the delivery program passing in -1 to indicate all info for all packages are to be returned and the time 17:00:00 is passed because (COMMENT CONTINUED DOWN BELOW)
            # this is the EOD time and the simulation should be completed by then and True is also passed to show total mileage for trucks
            print("Option 1 chosen!")
            print()
            startDeliveryProgram(-1, '17:00:00', True)
        elif userOption == 2: # if option 2 is chosen, also ask the user for the specified time the simulation is allowed to run up to
            print("Option 2 chosen!")
            print()
            userTime = input(
                "Please enter a time between 8:00:00 and 17:00:00 in the format 'HH:MM:SS' excluding the single quotes and press the enter key: ")
            print()
            startDeliveryProgram(-1, userTime, False)
        elif userOption == 3: # if option 3 is chosen, ask the user which specific package they want to know about by asking for package ID input and also ask the user for the specified time the simulation is allowed to run up to
            print("Option 3 chosen!")
            print()
            userPackID = input(
                "Please enter a packageID between 1-40 and press the enter key: ")
            userTime = input(
                "Please enter a time between 8:00:00 and 17:00:00 in the format 'HH:MM:SS' excluding the single quotes and press the enter key: ")
            print()
            startDeliveryProgram(int(userPackID), userTime, False)
        elif userOption == 4: # if option 4 is chosen, exit out of the loop and the program is over
            print("Quitting the delivery program!")
            print()
            break
        else:
            print("Invalid input, please enter a number within the specified range")
            print()

# executing python script calls the main function
main()