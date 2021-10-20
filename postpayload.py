from dataclasses import dataclass
from typing import Dict


@dataclass
class PostPayload:
    sub: str = None  # Must be provided
    title: str = None  # Must be provided
    text: str = ""  # Needs to be empty if it is a title only post, but None if it is a link post
    link: str = None
    image: str = None
    video: str = None
    parent: str = None
    flair_id: str = None
    flair_text: str = None
    collection_id: str = None
    sort: str = None
    comment_text: str = None
    date: str = "7,23"
    spoiler: bool = False
    nsfw: bool = False
    lock: bool = False
    contest: bool = False
    dont_notify: bool = False
    distinguish: bool = False
    sticky: bool = False
    lock_comment: bool = False
    distinguish_comment: bool = False
    sticky_comment: bool = False
    wait: bool = True

    _overrides_dict: Dict = None

    def get_overrides_dict(self) -> Dict:
        return self._overrides_dict

    @staticmethod
    def from_overrides(overrides_dict: Dict):
        # Use python black magic to convert the dictionary to our data class (overwriting only the provided fields)
        # for easy and consistent use
        payload = PostPayload(**overrides_dict)
        payload._overrides_dict = overrides_dict
        return payload
