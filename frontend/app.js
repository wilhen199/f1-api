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
  console.log(data);
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
  console.log(data);
}

/* ##### RESULTS ##### */

async function loadRaces(season) {
  const response = await fetch(`/api/races?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  console.log(data);
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
    <h2 class="view-title"> ${season} Races Result</h2>
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
  console.log(data);
}

async function loadDriverResults(season) {
  const response = await fetch(`/api/races?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  console.log(data);
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
    <h2 class="view-title"> ${season} Driver Results</h2>
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
  console.log(data);
}

async function loadTeamResults(season) {
  const response = await fetch(`/api/races?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  console.log(data);
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
    <h2 class="view-title"> ${season} Team Results</h2>
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
  console.log(data);
}

async function loadAwards(season) {
  const response = await fetch(`/api/races?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  console.log(data);
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
  console.log(data);
}
