# Dashop E-commerce Platform  

### Discription:   
>#### Dashop is a `B2C` E-commerce platform(coop project) which sells bags online.  

### Structure:    
>#### Django with front and back end seperation.  (Using `CORS`)
>* Frontend server is run by `Nginx` and it mainly tackles with requests for viewable resources (E.g. loading templates).  
>* Backend server mainly handles data processing functions and makes connections with third party applications.  
> It can adapt to requests from different sources (E.g. HTML, mobile, etc.) by using JSON as its unique data transfer method.


### Features:
>#### Register - supported by Oauth2
>* Register with personal information or register with a third-party account.
>#### Login - supported by JWT, SMTP, Celery
>* Login with registered account information or third-party authorized information. Login users will be remembered for certain of time and    
