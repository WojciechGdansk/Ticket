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
        let encodedDepartureCity = encodeURIComponent(departureCity.value)
        fetch(`/airports/airport?airport=${encodedDepartureCity}`).then(resp => {
        if (!resp.ok) {
            alert("Błąd")
        }
        return resp.json();
    })
        .then((resp)=>{
            let departFrom = resp.result[0]['iata']
            localStorage.setItem("departure", departFrom)
            })
        let encodedArrivalCity = encodeURIComponent(arrivalCity.value)
        fetch(`/airports/airport?airport=${encodedArrivalCity}` )
            .then(resp=>{
                if (!resp.ok) {
                    alert("Nie ma takiego lotniska")
                }
                return resp.json()
            })
            .then((resp)=>{
                let arriveTo = resp.result[0]['iata']
                localStorage.setItem('arrival', arriveTo)
            })

        if (localStorage.getItem('departure') === localStorage.getItem('arrival')) {
            alert("Wylot i przylot na to samo lotnisko- błąd")
        }
        window.location.href = `/routes/search?depart=${localStorage.getItem('departure')}&arrive=${localStorage.getItem('arrival')}&date=${flightDate.value}`
        localStorage.clear()

    }
    }
)
// if moush click somewhere on page hide search results
document.addEventListener('mouseup', function (ele) {
    if (!departureCity.contains(ele.target)) {
        departurelist.innerHTML = ''
    }
    else if (!arrivalCity.contains(ele.target)) {
            arrivallist.innerHTML = ''
    }
})
