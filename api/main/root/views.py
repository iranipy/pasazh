from main.utils import MetaApiViewClass, JsonValidation


class EmailAnnouncement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        followers = self.auth_req.get('/follow-user', params={'user_id': self.token_info['user_id']}, return_data=True)
g