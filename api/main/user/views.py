from main.utils import MetaApiViewClass, JsonValidation


class UpdateUserProfile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.auth_req.put('/user-profile', json=self.request.data)

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    def delete(self, request):
        self.auth_req.delete('/user-profile', params={'user_id': self.token_info['user_id']})


class Follow(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def get(self, request):
        self.auth_req.get('/follow-user', params={'user_id': self.token_info['user_id']})

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.auth_req.post('/follow-user', json=self.request.data)

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.token_info['user_id'], 'followed_user_id': data['followed_user_id']}
        self.auth_req.delete('/follow-user', params=params)


class Block(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def get(self, request):
        self.auth_req.get('/block-user', params={'user_id': self.token_info['user_id']})

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.auth_req.post('/block-user', json=self.request.data)

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.token_info['user_id'], 'banned_user_id': data['banned_user_id']}
        self.auth_req.delete('/block-user', params=params)
