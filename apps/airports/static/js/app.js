let departureCity = document.querySelector('#departure')
let arrivalCity = document.querySelector("#arrival")
let flightDate = document.querySelector("#date")

departureCity.addEventListener('keyup', ()=> {
    console.log(departureCity.value)
    if (departureCity.value.length !== 0) {
    fetch(`/airports/${departureCity.value}`).then(resp => {
        if (!resp.ok) {
            alert("Błąd")
        }
        return resp.json();
    })
        .then((resp)=>{
            console.log(resp)
        })
        }
})
