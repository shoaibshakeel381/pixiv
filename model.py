#!/usr/bin/env python3
from abc import abstractmethod, ABCMeta


class PixivModel(object):
    """
    store illust/novel data

    Attribute
    """
    __metaclass__ = ABCMeta

    def __init__(self, user=None):
        self.user = user

    @abstractmethod
    def from_data(self, data):
        """parse the data to a dict"""
        pass


class PixivIllustModel(PixivModel):
    @staticmethod
    def is_ranking(data):
        return 'works' in data or 'work' in data

    def extract_common_information(self, illust, data):
        if self.is_ranking(data):
            illust.rank = str(data['rank'])
            illust.previous_rank = str(data['previous_rank'])
            data = data['work']
        illust.id = str(data['id'])
        illust.user_id = str(data['user']['id'])
        illust.user_name = data['user']['name']
        illust.title = data['title']
        illust.small = data['image_urls']['small']
        illust.medium = data['image_urls']['medium']
        illust.large = data['image_urls']['large']
        illust.px_480mw = data['image_urls']['px_480mw']
        illust.px_128x128 = data['image_urls']['px_128x128']
        illust.views_count = data['stats']['views_count']
        illust.commented_count = data['stats']['commented_count']
        illust.score = data['stats']['score']
        illust.scored_count = data['stats']['scored_count']
        illust.public_favorited_count = data['stats']['favorited_count']['public']
        illust.private_favorited_count = data['stats']['favorited_count']['private']
        illust.user_name = data['user']['name']
        illust.user_account = data['user']['account']
        illust.user_profile_image_urls = data['user']['profile_image_urls']
        illust.sanity_level = data['sanity_level']
        illust.created_time = data['created_time']
        illust.type = data['type']
        illust.page_count = data['page_count']
        if illust.type == 'ugoira' and self.user:
            r = self.user.get_illustration(illust.id)
            illust.page_count = len(r[0]['metadata']['frames'])
        illust.is_manga = data['is_manga']
        illust.caption = data['caption']
        illust.tags = data['tags']
        return illust

    def get_image_url_per_illust(self, data):
        """
        get image_urls from one data
        """
        image_urls = []
        # extract work if the raw data is from ranking
        if 'work' in data:
            data = data['work']

        # not manga
        if self.page_count == 1:
            image_urls.append(data['image_urls']['large'])
        # manga
        else:
            for i in range(self.page_count):
                per_page_link = data['image_urls']['large'][:-5] + str(i) + data['image_urls']['large'][-4:]
                image_urls.append(per_page_link)
        return image_urls

    @classmethod
    def create_illust_from_data(cls, data, user=None):
        illust = cls(user)
        illust.extract_common_information(illust, data)
        image_urls = illust.get_image_url_per_illust(data)
        illust.image_urls = image_urls
        return illust

    @classmethod
    def from_data(cls, data_list, user=None):
        """parse data to dict contains illust information

        Return:
            result: a list of instance contains illust information
        """
        illusts = []
        for data in list(data_list):
            # ranking
            if cls.is_ranking(data):
                works = data['works']
                for work in works:
                    illust = cls.create_illust_from_data(work, user)
                    illusts.append(illust)

            # user_illusts or illust
            else:
                illust = cls.create_illust_from_data(data, user)
                illusts.append(illust)
        illusts = sorted(illusts, key=lambda object1: object1.id, reverse=True)
        return illusts
