import csv
import os
import re

import psycopg
from utils import GetConnectionString

from . import dataDirPath
from .linear_regression import perform2VariableLinearRegression


def UpdateModels():
    conn = psycopg.connect(GetConnectionString())
    cur = conn.cursor()

    dataFilenameFormat = re.compile("^([0-9]+)-([0-9]+).csv$")

    # will consist of tuples where the first element gives the file path, the second
    # element gives the first business area id and the third element gives the
    # second business area id.
    dataFileEntries = []

    for filename in os.listdir(dataDirPath):
        if (
            (dataFilenameMatch := dataFilenameFormat.match(filename)) is not None
            and (businessArea1Id := int(dataFilenameMatch.group(1))) <
            (businessArea2Id := int(dataFilenameMatch.group(2)))
        ):
            dataFileEntries.append(
                (
                    os.path.join(dataDirPath, filename),
                    businessArea1Id,
                    businessArea2Id
                )
            )

    for dataFileEntry in dataFileEntries:
        (dataFilePath, businessArea1Id, businessArea2Id) = dataFileEntry
        independentVariableValues = []
        dependentVariableValues = []

        try:
            with open(dataFilePath, "r") as dataFile:
                dataFileCsvReader = csv.reader(dataFile)
                next(dataFileCsvReader)  # ignore header line
                for dataRecord in dataFileCsvReader:
                    independentVariableValues.append(
                        tuple(
                            [int(e) for e in dataRecord[:2]]
                        )
                    )

                    dependentVariableValues.append(
                        float(dataRecord[2])
                    )
        except Exception as inst:
            print("An exception has occurred while trying to read the machine learning data from " + str(dataFileEntry) + ". This file will be skipped and the details of the exception will follow:")
            print(inst)
            continue

        recordCount = len(dependentVariableValues)

        # print(recordCount)
        # print(independentVariableValues)
        # print(dependentVariableValues)

        m1, m2, k = perform2VariableLinearRegression(recordCount, independentVariableValues, dependentVariableValues)

        print("---")
        print(businessArea1Id, businessArea2Id)
        print(m1, m2, k)
        # print(str(m1*5 + m2*30 + k))

        cur.execute("""SELECT * FROM RatingModel WHERE businessarea1id = %s AND 
        businessarea2id = %s;""", (businessArea1Id, businessArea2Id))

        if cur.fetchone() is None:
            cur.execute("""INSERT INTO RatingModel VALUES(%s,%s,%s,%s,%s);""",
                        (businessArea1Id, businessArea2Id, m1, m2, k))
        else:
            cur.execute("""UPDATE RatingModel SET skillOverlapCoefficient = %s, ageDifferenceCoefficient = %s, modelOffset = %s WHERE businessarea1id = %s AND 
            businessarea2id = %s;""",
                        (m1, m2, k, businessArea1Id, businessArea2Id))

        conn.commit()

    cur.close()
    conn.close()
