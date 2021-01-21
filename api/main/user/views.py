from main.utils import MetaApiViewClass, JsonValidation


class UpdateUserProfile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/user-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    def delete(self, request):
        self.del_req('/user-profile/', params={'user_id': self.user['id']})


class Follow(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def get(self, request):
        self.get_req('/follow-user/', params={'user_id': self.user['id']})

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/follow-user/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.user['id'], 'followed_user_id': data['followed_user_id']}
        self.del_req('/follow-user/', params=params)