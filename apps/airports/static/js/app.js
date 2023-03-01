let departureCity = document.querySelector('#departure')
let arrivalCity = document.querySelector("#arrival")
let flightDate = document.querySelector("#date")
let departurelist = document.querySelector('#departurelist')
let arrivallist = document.querySelector('#arrivallist')
let elementLi = document.querySelector('#element-li')
let elementLiArrival = document.querySelector('#element-li-arrival')

departureCity.addEventListener('keyup', ()=> {
    departurelist.innerHTML = ''
    if (departureCity.value.length !== 0) {
    fetch(`/airports/`, {headers: {"airport": `${departureCity.value}`}}).then(resp => {
        if (!resp.ok) {
            alert("Błąd")
        }
        return resp.json();
    })
        .then((resp)=>{

            if (resp.result.length>0) {
                departurelist.style = "block"
                for (let i= 0; i<resp.result.length;i++) {
                    let newli = elementLi.cloneNode(true)
                    newli.style =  "block"
                    newli.className = "departure-li"
                    newli.innerHTML = `${resp.result[i]['city']}, ${resp.result[i]['location_name']}, <small>${resp.result[i]['iata']}, ${resp.result[i]['country']}</small>`
                    newli.addEventListener('click', ()=>{
                        departurelist.innerHTML = ''
                        departureCity.value = `${resp.result[i]['iata']}, ${resp.result[i]['location_name']}, ${resp.result[i]['country']}`})
                    departurelist.appendChild(newli)
                }
            }
            else  {
                departurelist.style = "none"
            }

        })
        }
})


arrivalCity.addEventListener('keyup', ()=> {
    arrivallist.innerHTML = ''
    if (arrivalCity.value.length !== 0) {
    fetch(`/airports/`, {headers: {'airport': `${arrivalCity.value}`}}).then(resp => {
        if (!resp.ok) {
            alert("Błąd")
        }
        return resp.json();
    })
        .then((resp)=>{
            if (resp.result.length>0) {
                arrivallist.style = "block"
                for (let i= 0; i<resp.result.length;i++) {
                    let newli = elementLiArrival.cloneNode(true)
                    newli.style =  "block"
                    newli.className = "departure-li"
                    newli.innerHTML = `${resp.result[i]['city']}, ${resp.result[i]['location_name']}, <small>${resp.result[i]['iata']}, ${resp.result[i]['country']}</small>`
                    newli.addEventListener('click', ()=>{
                        arrivallist.innerHTML = ''
                        arrivalCity.value = `${resp.result[i]['iata']}, ${resp.result[i]['location_name']}, ${resp.result[i]['country']}`})
                    arrivallist.appendChild(newli)
                }
            }
            else  {
                arrivallist.style = "none"
            }

        })
        }
})
