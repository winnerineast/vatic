import os.path, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from turkic.server import handler, application
from turkic.database import Session
import cStringIO
from models import *

@handler()
def getjob(id, training):
    job = Session.query(Job).get(id)
    segment = job.segment
    video = segment.video
    labels = dict((l.id, l.text) for l in video.labels)

    return {"start":        segment.start,
            "stop":         segment.stop,
            "slug":         video.slug,
            "width":        video.width,
            "height":       video.height,
            "skip":         video.skip,
            "perobject":    video.perobjectbonus,
            "completion":   video.completionbonus,
            "jobid":        job.id,
            "labels":       labels,
            "training":     training}

@handler(post = "json")
def savejob(id, training, tracks):
    job = Session.query(Job).get(id)

    if training:
        replacement = job.markverified(True)
        replacement.publish()
        Session.add(replacement)

    for label, track in tracks:
        path = Path(job = job)
        path.label = Session.query(Label).get(label)

        for frame, userbox in track.items():
            box = Box(path = path)
            box.xtl = userbox[0]
            box.ytl = userbox[1]
            box.xbr = userbox[2]
            box.ybr = userbox[3]
            box.occluded = userbox[4]
            box.outside = userbox[5]
            box.frame = frame
            path.boxes.append(box)
        job.paths.append(path)

    Session.add(job)
    Session.commit()
    return True
