from typing import Optional, List

from pydantic import BaseModel


class StatData(BaseModel):
    time: Optional[int]
    value: Optional[int]


class GetStatTrends(BaseModel):
    comments: Optional[List[StatData]]
    complaints: Optional[List[StatData]]
    content_opens: Optional[List[StatData]]
    engagement: Optional[List[StatData]]
    feedback: Optional[List[StatData]]
    hides_from_feed: Optional[List[StatData]]
    left_members: Optional[List[StatData]]
    likes: Optional[List[StatData]]
    link_clicks: Optional[List[StatData]]
    members_count: Optional[List[StatData]]
    members_diff: Optional[List[StatData]]
    music_plays: Optional[List[StatData]]
    negatives: Optional[List[StatData]]
    new_members: Optional[List[StatData]]
    new_members_target: Optional[List[StatData]]
    page_visits: Optional[List[StatData]]
    photo_opens: Optional[List[StatData]]
    reach: Optional[List[StatData]]
    reach_earned: Optional[List[StatData]]
    reach_mob: Optional[List[StatData]]
    reach_mobweb: Optional[List[StatData]]
    reach_own: Optional[List[StatData]]
    reach_web: Optional[List[StatData]]
    renderings: Optional[List[StatData]]
    reshares: Optional[List[StatData]]
    topic_opens: Optional[List[StatData]]
    video_plays: Optional[List[StatData]]
    votes: Optional[List[StatData]]
