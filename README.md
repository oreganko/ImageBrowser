# ImageBrowser

## Run application with docker-compose
1. To run the application, in root directory run
`docker-compose up`
2.  open `0.0.0.0:8000` in your browser.
3. Then app is ready to use and one ADMIN user is created. 
   Admin can use any of system functionalities. 
   You can log in with `login=admin` and `password=admin`

## Using the system
### Users creation
1. To create standard users, open `0.0.0.0:8000/admin` with admin user and
   add new user:
   - click 'Add User' in admin panel
   - input user's username, password and choose plan for user
     (You can choose between builtin Basic, Premium, Enterprise or create your own plan in PlanTier tab)
   - save user, you don't have to set anything more for them

### Plan Tiers creation
1. In admin panel open PlanTiers tab and click to create a new one.
2. You have to input plan name (it has to be a unique name), 
   add and choose thumbnail sizes (use ctrl+mouseclick to choose size from list), check if your plan gives the ability to see an original image and the possibility to fetch expiring link.


### Images upload and list
1. `0.0.0.0:8000/` is a root of the api. You can choose 
if you want to upload an image `0.0.0.0:8000/images/upload` or see the list of uploaded images `0.0.0.0:8000/images`.
2. After uploading a file (or when listing files) you can see some links, dependent on your user plan:
   - thumbnail links (links to see thumbnails with size given in the plan; note that thumbnails can be only smaller or equal than original image)
   - original file link (link to see your original file)
   - link to page where you can fetch expiring link

### Create expiring link
If it is in your plan, you can fetch the expiring link with the binary od image.
1. Open list of images `0.0.0.0:8000` and click the link under `create_expiring_link` for image you currently want to fetch the link for
2. Now you have to input seconds after which the link will expire. You can choose any between 300 and 30000.


## Future work - cache
This app does not contain caching. In some views many SQL queries are run, so with many customers it would cause server overload.
Redis and Memcached were tested in this app, but it broke authentication (session problems probably) and image viewing. 
Due to the short remaining time, I decided to not use it in any queries and check it the other time. 
But if I could, I would add cacheing within list view and sql queries for getting ImageInstance model.


