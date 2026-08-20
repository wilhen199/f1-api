/* ##### BEGINNING ##### */

document.addEventListener("DOMContentLoaded", () => {
  console.log("F1 app loaded!");
  loadSeason()
  renderTabsBar()

  document.getElementById("navStandings").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "flex"
    const season = document.getElementById("seasonSelect").value
    if (currentTab === "Drivers") {loadStandingsDrivers(season);}
    else {loadStandingsTeams(season)}
  })

    document.getElementById("navResults").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "none"
    const season = document.getElementById("seasonSelect").value
    document.getElementById("content").innerHTML = "<h1>Round Results Soon</h1>"
  })
})

/* ##### VARIABLES ##### */
let currentTab = "Drivers"


/* ##### MENU - TABS ##### */

async function renderTabsBar() {
  const tabBar = document.getElementById("tabsBar")
  const tabs = ["Drivers", "Teams"]
  for (const i of tabs) {

    const tab = document.createElement("div")
    tab.textContent = i
    tab.className = "tab"
    tabBar.appendChild(tab)
    tab.addEventListener("click", () => {
      currentTab = i
    const season = document.getElementById("seasonSelect").value
    console.log(i)
    if (i === "Drivers") {loadStandingsDrivers(season);}
    else 
    {loadStandingsTeams(season);}
  })
  }
}

async function loadSeason() {
  const response = await fetch("/api/seasons")
  const seasons = await response.json()

  const select = document.getElementById("seasonSelect")
  select.innerHTML = ''

  for (const season of seasons) {
    const option = document.createElement("option")
    option.value = season
    option.textContent = season
    select.appendChild(option)
  }
  select.addEventListener("change", () => {
    if (currentTab === "Drivers") {loadStandingsDrivers(select.value);}
    else {loadStandingsTeams(select.value);}
    })

  loadStandingsDrivers(select.value)
}

async function loadStandingsDrivers(season) {
  const response = await fetch(`/api/standings/drivers?season=${season}`)
  const data = await response.json()
  const content = document.getElementById('content')
  content.innerHTML = ''
  for (const row of data.rows) {
    content.innerHTML += `
    <p>
    ${row.position} -
    ${row.driver.givenName} 
    ${row.driver.familyName} -
    ${row.driver.nationality} -
    ${row.team.name} -
    ${row.points} pts -
    ${row.wins} pts
    </p>`
  }
  console.log(data)
}

async function loadStandingsTeams(season) {
  const response = await fetch(`/api/standings/teams?season=${season}`)
  const data = await response.json()
  const content = document.getElementById('content')
  content.innerHTML = ''
  for (const row of data.rows) {
    content.innerHTML += `
    <p>
    ${row.position} -
    ${row.team.name} -
    ${row.team.nationality} -
    ${row.points} pts -
    ${row.wins} pts
    </p>`
  }
  console.log(data)
}

