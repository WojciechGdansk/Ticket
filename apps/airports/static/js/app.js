let departureCity = document.querySelector('#departure')
let arrivalCity = document.querySelector("#arrival")
let flightDate = document.querySelector("#date")
let departurelist = document.querySelector('#departurelist')
let arrivallist = document.querySelector('#arrivallist')
let elementLi = document.querySelector('#element-li')
let elementLiArrival = document.querySelector('#element-li-arrival')
let submitButton = document.querySelector('#submit-button')
let datainput = document.querySelectorAll('.fields-to-fill')

departureCity.addEventListener('keyup', ()=> {
    departurelist.innerHTML = ''
    if (departureCity.value.length !== 0) {
    let encodedDepartureCity = encodeURIComponent(departureCity.value)
    fetch(`/airports/airport?airport=${encodedDepartureCity}`).then(resp => {
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
    let encodedArrivalCity = encodeURIComponent(arrivalCity.value)
    fetch(`/airports/airport?airport=${encodedArrivalCity}` ).then(resp => {
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

submitButton.addEventListener('click', ()=>{
    if (departureCity.value.length<1 || arrivalCity.value.length < 1 || flightDate.value.length <1) {
        alert("Uzupełnij wszystkie pola")
    }
    else {
        send()
    }

    }
)

async function checkAirport(airport) {
        const encodedCity = encodeURIComponent(airport)
        const response = await fetch(`/airports/airport?airport=${encodedCity}`)
        if (!response.ok) {
            alert("Błąd")
            return
        }
        const data = await response.json()
        return data.result[0]['iata']

}

async function send() {
    const departureAirport = await checkAirport(departureCity.value)
    const arriveAirport = await checkAirport(arrivalCity.value)
    window.location.href = `/routes/search?depart=${departureAirport}&arrive=${arriveAirport}&date=${flightDate.value}`
}