from django.core.cache import caches

#参数 key_prefix, key_param, expire(time),cache(where)
def cache_check(**cache_kwargs):
    def _cache_check(func):
        def wrapper(self,request,*args,**kwargs):
            CACHE = caches['default']
            if "cache" in cache_kwargs:
                CACHE = caches[cache_kwargs['cache']]
            key_prefix = cache_kwargs['key_prefix']
            #用key_param传过来的做唯一标识
            key_param = cache_kwargs['key_param']
            expire = cache_kwargs.get('expire',30)
            # '/detail/1' -> def get(self,request,sku_id)
            if key_param not in kwargs:
                raise
            cache_key = key_prefix + kwargs[key_param]
            print('cache_key is %s'%(cache_key))
            res = CACHE.get(cache_key)
            if res:
                print('return %s cache'%(cache_key))
                return res
            #没有缓存
            res = func(self,request,*args,**kwargs)
            CACHE.set(cache_key,res,expire)
            return res
        return wrapper
    return _cache_check