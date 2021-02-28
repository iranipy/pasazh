from main.utils import MetaApiViewClass, JsonValidation


class EmailAnnouncement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        followers = self.get_req('/follow-user/', params={'user_id': self.user['id']}, return_data=True)
        return self.success(data={' ': followers})
