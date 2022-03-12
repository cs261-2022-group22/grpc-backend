import os

import psycopg
from utils import GetConnectionString

from . import DataDirectory

conn = psycopg.connect(GetConnectionString())
cur = conn.cursor()


def processPendingRatingFeedback(businessArea1Id, businessArea2Id, skillOverlap, ageDifference, rating):
    newEntry = ",".join([str(skillOverlap), str(ageDifference), str(rating)]) + "\n"

    dataFileName = str(businessArea1Id) + "-" + str(businessArea2Id) + ".csv"
    dataFilePath = os.path.join(DataDirectory, dataFileName)

    if not os.path.isfile(dataFilePath):
        with open(dataFilePath, "w") as f:
            f.write("SkillOverlap,AgeDifference,Rating\n")

    with open(dataFilePath, "a") as f:
        f.write(newEntry)

    print(__file__, "COMPLETE (1 record)")


def ProcessPendingRating():
    cur.execute("""DELETE FROM PendingRatingFeedback RETURNING businessarea1id, businessarea2id, skillOverlap, ageDifference, rating;""")
    rows = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()
    for row in rows:
        processPendingRatingFeedback(row[0], row[1], row[2], row[3], row[4])
