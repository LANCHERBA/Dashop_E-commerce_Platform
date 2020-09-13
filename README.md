# Dashop E-commerce Platform  

### Discription:   
>#### Dashop is a `B2C` E-commerce platform(coop project) which sells bags online.  

### Structure:    
>#### Framework: Django with front and back end seperation  (Using `CORS`)
>* Frontend server is run by `Nginx` and it mainly tackles with requests for viewable resources (E.g. loading templates).  
> Also, it will call backend server using Ajax for needed data.
>* Backend server mainly handles data processing functions and makes connections with third party applications.  
> It can adapt to requests from different sources (E.g. HTML, mobile, etc.) by using `JSON` as its unique data transfer method.  
>#### Data Storage
>* Redis for cache.
>* MySQL for other data (E.g. goods info, payment related data).


### Features:
>#### Register - supported by Oauth2, SMTP, Celery
>* Register with personal information or register with a third-party account.  
>* Verification emails will be sent by SMTP server and Celery is used to handle this task.
>#### Login - supported by JWT
>* Login with registered account information. Users will be remembered for certain of time after they login to their accounts.    
>#### Show goods/shopping carts info - supported by Redis
>* Cache is used to improve the data loading efficiency. Cache will be updated when changes on data occur. 
>#### Payment - supported by Alipay
>* Paying processes are supported by Alipay.
