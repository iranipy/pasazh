from main.utils import MetaApiViewClass, JsonValidation


class UpdateUserProfile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.put_req('/user-profile/', json_str=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    def delete(self, request):
        self.del_req('/user-profile/', params={'user_id': self.token_info['user_id']})


class Follow(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def get(self, request):
        self.get_req('/follow-user/', params={'user_id': self.token_info['user_id']})

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.post_req('/follow-user/', json_str=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.token_info['user_id'], 'followed_user_id': data['followed_user_id']}
        self.del_req('/follow-user/', params=params)


class Block(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def get(self, request):
        self.get_req('/block-user/', params={'user_id': self.token_info['user_id']})

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.post_req('/block-user/', json_str=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.token_info['user_id'], 'banned_user_id': data['banned_user_id']}
        self.del_req('/block-user/', params=params)
