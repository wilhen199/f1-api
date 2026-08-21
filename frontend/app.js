/* ##### BEGINNING ##### */

document.addEventListener("DOMContentLoaded", () => {
  console.log("F1 app loaded!");
  loadSeason();
  renderTabsBar("standings");
  document.getElementById("navStandings").classList.add("active");

  document.getElementById("navStandings").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("standings");
    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navStandings").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    if (currentTabStandigs === "Drivers") {
      loadStandingsDrivers(season);
    } else {
      loadStandingsTeams(season);
    }
  });

  document.getElementById("navResults").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "flex";

    renderTabsBar("results");

    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navResults").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    if (currentTabResults === "Races") {
      loadRaces(season);
    } else if (currentTabResults === "Driver") {
      loadDriverResults(season);
    } else if (currentTabResults === "Team") {
      loadTeamResults(season);
    } else {
      loadAwards(season);
    }
  });
});

/* ##### VARIABLES AND UTILITIES ##### */
let currentTabStandigs = "Drivers";
let currentTabResults = "Races";

function badge(position) {
  const pos = Number(position);
  if (pos === 1) {
    return '<span class="badge pos-1">1</span>';
  } else if (pos === 2) {
    return '<span class="badge pos-2">2</span>';
  } else if (pos === 3) {
    return '<span class="badge pos-3">3</span>';
  }
  return `<span class="badge">${pos}</span>`;
}

function initials(name) {
  const words = name.split(" ");
  let result = "";
  for (const word of words) {
    result += word[0];
  }
  return result;
}

/* ##### MENU - TABS ##### */

async function renderTabsBar(view = "standings") {
  const tabBar = document.getElementById("tabsBar");
  tabBar.innerHTML = "";
  let tabToDisplay = [];
  if (view === "standings") {
    tabToDisplay = ["Drivers", "Teams"];
  } else if (view === "results") {
    tabToDisplay = ["Races", "Driver", "Team", "Awards"];
  }

  for (const i of tabToDisplay) {
    const tab = document.createElement("div");
    tab.textContent = i;
    tab.className = "tab";

    if ((view === "standings" && i === currentTabStandigs) || (view === "results" && i === currentTabResults)) {
      tab.classList.add("active");
    }

    tab.addEventListener("click", () => {
      const allTabs = document.querySelectorAll(".tab");
      for (const t of allTabs) {
        t.classList.remove("active");
      }
      tab.classList.add("active");

      const season = document.getElementById("seasonSelect").value;

      if (view === "standings") {
        currentTabStandigs = i;
        if (i === "Drivers") {
          loadStandingsDrivers(season);
        } else {
          loadStandingsTeams(season);
        }
      } else if (view === "results") {
        currentTabResults = i;
        if (i === "Races") {
          loadRaces(season);
        } else if (i === "Driver") {
          loadDriverResults(season);
        } else if (i === "Team") {
          loadTeamResults(season);
        } else {
          loadAwards(season);
        }
      }
    });
    tabBar.appendChild(tab);
  }
}

async function loadSeason() {
  const response = await fetch("/api/seasons");
  const seasons = await response.json();

  const select = document.getElementById("seasonSelect");
  select.innerHTML = "";

  for (const season of seasons) {
    const option = document.createElement("option");
    option.value = season;
    option.textContent = season;
    select.appendChild(option);
  }
  select.addEventListener("change", () => {
    const currentView = document.querySelector(".nav-link.active").id.replace("nav", "").toLowerCase();
    if (currentView === "standings") {
      const currentTab = document.querySelector("#tabsBar .tab.active").textContent;
      if (currentTab === "Drivers") {
        loadStandingsDrivers(select.value);
      } else {
        loadStandingsTeams(select.value);
      }
    } else if (currentView === "results") {
      const currentTab = document.querySelector("#tabsBar .tab.active").textContent;
      if (currentTab === "Races") {
        loadRaces(select.value);
      } else if (currentTab === "Driver") {
        loadDriverResults(select.value);
      } else if (currentTab === "Team") {
        loadTeamResults(select.value);
      } else {
        loadAwards(select.value);
      }
    }
  });

  loadStandingsDrivers(select.value);
}

/* ##### STANDIGS ##### */

async function loadStandingsDrivers(season) {
  const response = await fetch(`/api/standings/drivers?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const row of data.rows) {
    rowsHTML += `
    <tr>
      <td>${badge(row.position)}</td>
      <td><img class="avatar" src="${row.driver.photo}"> <a href="/driver/${row.driver.id}?season=${season}">${row.driver.givenName} ${row.driver.familyName}</a></td>
      <td><img class="flagimg" src="${row.driver.flag}"></td>
      <td>
        ${row.team.photo ? `<img class="avatar" src="${row.team.photo}">` : `<span class="avatar-fallback">${initials(row.team.name)}</span>`}
        <a href="/team/${row.team.id}?season=${season}">${row.team.name}</a>
      </td>
      <td>${row.points}</td>
      <td>${row.wins}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Driver Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>NAT</th>
          <th>TEAM</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadStandingsTeams(season) {
  const response = await fetch(`/api/standings/teams?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const row of data.rows) {
    rowsHTML += `
    <tr>
      <td>${badge(row.position)}</td>
      <td>
        ${row.team.photo ? `<img class="avatar" src="${row.team.photo}">` : `<span class="avatar-fallback">${initials(row.team.name)}</span>`}
        <a href="/team/${row.team.id}?season=${season}">${row.team.name}</a>
    </td>
      <td><img class="flagimg" src="${row.team.flag}"></td>
      <td>${row.points}</td>
      <td>${row.wins}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Team Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>TEAM</th>
          <th>NAT</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

/* ##### RESULTS ##### */

async function loadRaces(season) {
  const response = await fetch(`/api/results?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const row of data.rows) {
    rowsHTML += `
    <tr>
      <td><img class="flagimg" src="${row.flag}"></td>
      <td><a href="/race/${row.round}?season=${season}">${row.raceName}</a></td>
      <td>${row.circuit}</td>
      <td>${row.date}</td>
      <td>${row.laps}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Races List</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>GRAND PRIX</th>
          <th>CIRCUIT</th>
          <th>DATE</th>
          <th>LAPS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadDriverResults(driverId, season) {
  const response = await fetch(`/api/driver/${driverId}?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  const driverName = `${data.driver.givenName} ${data.driver.familyName}`;
  const driverPhoto = data.driver.photo;
  const driverFlag = data.driver.flag;
  const info = data.driver.info;
  const pos = data.position;
  const pts = data.points;
  const wins = data.wins;

  for (const race of data.races) {
    const round = race.round;
    const raceName = race.raceName;
    const flagRace = race.flag;
    const teamName = race.team.name;
    const teamPhoto = race.team.photo;
    const teamId = race.team.id;
    const grid = race.grid;
    const result = race.position;
    const ptsRace = race.points;
    const status = race.status;

    rowsHTML += `
    <tr>
      <td>${round}</td>
      <td><img src="${flagRace}"> <a href="/race/${round}?season=${season}">${raceName}</a></td>
      <td><img src="${teamPhoto}"> <a href="/team/${teamId}?season=${season}">${teamName}</a></td>
      <td><span class"badge">${grid}</span></td>
      <td<span class"badge">${result}</span></td>
      <td>${ptsRace}</td>
      <td>${status}</td>
    </tr>`;
  }
  content.innerHTML += `
    <div class="profile">
      <img class="avatar" src="${driverPhoto}">
      <div class="profile-info">
        <h2>${driverName}  <img class="flagimg" src="${driverFlag}">
        </h2>
      <div class="profile-stats">
        <div>Position: ${pos}</div>
        <div>Points: ${pts}</div>
        <div>Wins: ${wins}</div>
      </div>
      <a href="${info}"><p>Info 🌐</p></a>
    </div>
    <h3> ${season} SEASON RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>TEAM</th>
          <th>GRID</th>
          <th>RESULT</th>
          <th>PTS</th>
          <th>STATUS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadTeamResults(teamId, season) {
  const response = await fetch(`/api/team/${teamId}?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  const teamName = data.team.name;
  const teamPhoto = data.team.photo;
  const teamFlag = data.team.flag;
  const info = data.team.info;
  const pos = data.position;
  const pts = data.points;
  const wins = data.wins;
  const driverOne = data.drivers[0].driver;
  const driverTwo = data.drivers[1].driver;

  for (const race of data.races) {
    const round = race.round;
    const raceName = race.raceName;
    const flagRace = race.flag;
    for (item of race.drivers) {
      const driverId = item.driver.id;
      const driverName = `${item.driver.givenName} ${item.driver.familyName}`;
      const driverPos = item.position;
      const driverPts = item.points;
      const driverStatus = item.status;

      return [driverId, driverName, driverPos, driverPts, driverStatus];
    }

    rowsHTML += `
    <tr>
      <td>${round}</td>
      <td><img src="${flagRace}"> <a href="/race/${round}?season=${season}">${raceName}</a></td>
      <td>
        <div> 
          <a href="#/driver/${driverId}?season=${season}">${driverName}</a>
          <span class="badge">${driverPos}</span>
          ${driverPts} pts
          ${driverStatus}
        </div>
      </td>
    </tr>`;
  }
  content.innerHTML += `
    <div class="profile">
      <img class="avatar" src="${teamPhoto}">
      <div class="profile-info">
        <h2>${teamName}  <img class="flagimg" src="${teamFlag}">
        </h2>
      <div>
        <a href="/driver/${driverOne.id}?season=${season}"><img class="avatar-small" src="${driverOne.photo}">${driverOne.givenName} ${driverOne.familyName}</a>
      </div>
      <div>
        <a href="/driver/${driverTwo.id}?season=${season}"><img class="avatar-small" src="${driverTwo.photo}">${drivertwo.givenName} ${driverTwo.familyName}</a>
      </div>
      <div class="profile-stats">
        <div>Position: ${pos}</div>
        <div>Points: ${pts}</div>
        <div>Wins: ${wins}</div>
      </div>
      <a href="${info}"><p>Info 🌐</p></a>
    </div>
    <h3> ${season} GP RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>DRIVERS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadAwards(season) {
  const response = await fetch(`/api/awards?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const race of data) {
    const round = race.round;
    const raceName = race.raceName;
    const circuit = race.Circuit.circuitName;
    const date = race.date;
    const laps = race.laps;
    const country = race.Circuit.Location.country;

    rowsHTML += `
    <tr>
      <td>${country}</td>
      <td><a href="/race/${round}?season=${season}">${raceName}</a></td>
      <td>${circuit}</td>
      <td>${date}</td>
      <td>${laps}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Awards</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>GRAND PRIX</th>
          <th>CIRCUIT</th>
          <th>DATE</th>
          <th>LAPS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}
