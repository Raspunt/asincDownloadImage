import asyncio
import aiohttp

from model import *
from flask import Flask , render_template ,request,redirect


app = Flask(__name__,
            static_folder='static')


global photo_List
photo_List = []

photoId = 0
dBtn = False



async def CheckStatus(current_page,query):
    header = {"Authorization":'563492ad6f917000010000016d7535a952354a49bda7c3844cade612'}

    global dBtn

    if len(photo_List) != 0 and dBtn == True :
        photo_List.clear()
        print("Очистить")
        dBtn = False

    global photoId   
    


    async with aiohttp.ClientSession(headers=header) as client :
        url = f'https://api.pexels.com/v1/search?query={query}&page={current_page}&per_page=1'
        async with  client.get(url) as resp:
            print(resp.status)
            rj = await resp.json()
            for el in rj['photos']:
                # print(el['src']['original'])
                photoId = photoId + 1
                photo = Photo(photoId,el['src']['original'])
                photo_List.append(photo)
                print(f'{el.index} это  цифра' )
            

        return photo_List
       

           
            




async def main(query,page_count):
    # page_count = int(input('Count page '))

    queue = asyncio.Queue()
    task_list = []
    current_page = 0
    while current_page < page_count:
        current_page += 1
        task = asyncio.create_task(CheckStatus(current_page,query))
        task_list.append(task)
    await queue.join()
    await asyncio.gather(*task_list,return_exceptions=True)

    
    print('ВСе!')


@app.route('/',methods=['POST'])
def FlaskHello():
    print(request.form)
    sq = request.form.get('sq')
    page_count = request.form.get('page_count')
    if sq != '' and sq != None and page_count != '' and page_count != None:
        asyncio.run(main(sq,int(page_count)))

    return render_template('index.html',imgs=photo_List)
    

@app.route('/',methods =['GET'])
def StartPage():
    return render_template('index.html')


@app.route('/download/<imageid>',methods =['GET'])
def downloadImage(imageid):
    global dBtn
    imageUrl = photo_List[int(imageid)]
    dBtn = True
    return render_template('download.html',imageUrl=imageUrl)





# asyncio.run(main())

if __name__ == '__main__':
    app.config["CACHE_TYPE"] = "null"
    app.debug = True
    app.run()
