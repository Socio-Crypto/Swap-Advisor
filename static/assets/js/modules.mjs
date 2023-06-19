// #region fetch the core modules //
var modules = {};
async function load() {
  return await fetch(window.location.origin + "/static/assets/html/modules.html")
    .then(function (response) {
      return response.text();
    })
    .then(function (html) {
      let parser = new DOMParser();
      return parser.parseFromString(html, "text/html");
    })
    .catch(function (err) {
      console.log("Failed to fetch the addons modules: ", err);
      return;
    });
}
async function load1() {
  let a = await fetch(window.location.origin + "/static/assets/html/modules.html");
  let b = await a.text();
  let parser = new DOMParser();
  let c = parser.parseFromString(b, "text/html");
  return c;
}
export async function caller() {
  modules["addons"] = await load1();
  startModule();
}
// caller();
// #endregion fetch the core modules //

var moduleInfo = {};
var moduleData = {};

function startModule() {
  function preprocessData() {
    moduleData.nodes = JSON.parse(
      document.getElementById("nodes").value.replaceAll("'", '"')
    ).sort((a, b) => {
      return compare(a, b, "id");
    });

    moduleData.links = JSON.parse(
      document.getElementById("links").value.replaceAll("'", '"')
    );

    moduleData.source = JSON.parse(
      document.getElementById("data_of_source_chain").value.replaceAll("'", '"')
    ).sort((a, b) => {
      return compare(a, b, "date");
    });

    moduleData.destination = JSON.parse(
      document
        .getElementById("data_of_destination_chain")
        .value.replaceAll("'", '"')
    ).sort((a, b) => {
      return compare(a, b, "date");
    });

    let date1 = "";
    moduleData.nodeList = {};
    const datainit = new Array(moduleData.nodes.length).fill(0);
    for (i = 0; i < moduleData.nodes.length; i++) {
      moduleData.nodeList[moduleData.nodes[i].id] = i;
    }

    moduleData.sourceStacked = [];
    moduleData.sourceStacked100 = [];
    moduleData.source.forEach((x) => {
      if (x.date != date1) {
        date1 = x.date;
        moduleData.sourceStacked.push([x.date, ...datainit]);
        moduleData.sourceStacked[moduleData.sourceStacked.length - 1][
          moduleData.nodeList[x.sourcechain] + 1
        ] = x.value;
      } else {
        moduleData.sourceStacked[moduleData.sourceStacked.length - 1][
          moduleData.nodeList[x.sourcechain] + 1
        ] = x.value;
      }
    });
    moduleData.sourceStacked100 = moduleData.sourceStacked.map((obj) => {
      const [id, ...rest] = obj;
      const sum = rest.reduce((acc, val) => acc + val);
      return [sum, id, ...rest];
    });
    moduleData.sourceStacked100 = moduleData.sourceStacked100.map((obj) => {
      const [sum, id, ...rest] = obj;
      const rest2 = rest.map((val) => val / sum || 0);
      return [sum, id, ...rest2];
    });
    moduleData.sourceStacked100.forEach((array) => array.splice(0, 1));

    moduleData.destinationStacked = [];
    moduleData.destinationStacked100 = [];
    date1 = '';
    moduleData.destination.forEach((x) => {
      if (x.date != date1) {
        date1 = x.date;
        moduleData.destinationStacked.push([x.date, ...datainit]);
        moduleData.destinationStacked[moduleData.destinationStacked.length - 1][
          moduleData.nodeList[x.destinationchain] + 1
        ] = x.value;
      } else {
        moduleData.destinationStacked[moduleData.destinationStacked.length - 1][
          moduleData.nodeList[x.destinationchain] + 1
        ] = x.value;
      }
    });
    moduleData.destinationStacked100 = moduleData.destinationStacked.map(
      (obj) => {
        const [id, ...rest] = obj;
        const sum = rest.reduce((acc, val) => acc + val);
        return [sum, id, ...rest];
      }
    );
    moduleData.destinationStacked100 = moduleData.destinationStacked100.map(
      (obj) => {
        const [sum, id, ...rest] = obj;
        const rest2 = rest.map((val) => val / sum || 0);
        return [sum, id, ...rest2];
      }
    );
    moduleData.destinationStacked100.forEach((array) => array.splice(0, 1));

    moduleData.color = [
      "#c23531",
      "#2f4554",
      "#61a0a8",
      "#d48265",
      "#91c7ae",
      "#749f83",
      "#ca8622",
      "#bda29a",
      "#6e7074",
      "#546570",
      "#c4ccd3",
    ];
    moduleData.vars = {
      svgurl: "./static/images/",
      forcechart: {
        title: "Asset Flow Network",
      },
      sankychart: {
        title: "Flow Diagarm",
      },
      chart1: {
        title: "Total Volume Of Bridge",
      },
      chart3: {
        title: "Daily Volume Of Bridge by Source - axlUSDC",
      },
      chart4: {
        title: "Daily Volume Of Bridge by Target - axlUSDC",
      },
      chart5: {
        title: "Normalized Daily Volume Of Bridge by Source",
      },
      chart6: {
        title: "Normalized Daily Volume Of Bridge by Target",
      },
    };

    function compare(a, b, key) {
      if (a[key] < b[key]) {
        return -1;
      } else if (a[key] > b[key]) {
        return 1;
      } else {
        return 0;
      }
    }
  }

  preprocessData();

  moduleManage().loadModules([
    { core: "addons", name: "sankeychart" },
    { core: "addons", name: "forcechart" },
    { core: "addons", name: "chart1" },
    { core: "addons", name: "chart3" },
    { core: "addons", name: "chart4" },
    { core: "addons", name: "chart5" },
    { core: "addons", name: "chart6" },
  ]);

  // #region add-ons loading //
  function moduleManage() {
    const load = (module) => {
      module = { ...module, ...{ script: "", method: {}, event: {} } };
      let src = modules[module.core].getElementById(module.name + "-container");
      let des = document.getElementById(module.name + "-container");
      des.innerHTML = src.innerHTML;
      if (des.querySelector("script") != undefined)
        eval("module.script = " + des.querySelector("script").innerHTML.trim());
      return module;
    };
    const loadModule = (module) => {
      if (moduleInfo[module.name] == undefined) {
        module = load(module);
        module.init = eval("moduleHandle_" + module.name);
        module.method = module.script(); //();
        moduleInfo[module.name] = {
          core: module.core,
          name: module.name,
          script: module.script,
          method: module.method.method,
          init: module.init,
        };
        module.ret = module.init();
        moduleInfo[module.name].method.setCallback(module.ret.event);
        moduleInfo[module.name].event = module.ret.event;
      } else {
        module = moduleInfo[module.name];
        module.ret = module.init();
      }
    };
    const unloadModule = (moduleName) => {
      let des = document.getElementById(moduleName + "-container");
      des.innerHTML = "";
      delete moduleInfo[moduleName];
    };
    return {
      loadModules: function (moduleList) {
        moduleList.forEach((module) => loadModule(module));
      },
      loadModule: loadModule,
      unloadModuleAll: function () {
        Object.keys(moduleInfo).forEach((moduleName) =>
          unloadModule(moduleName)
        );
      },
      unloadModule: unloadModule,
    };
  }
  function visibility() {
    return {
      hideForm: function (form) {
        document.getElementById(form + "-container").style.display = "none";
      },
      showForm: function (form) {
        let node = document.getElementById(form + "-container");
        while (node.tagName != "BODY") {
          node.style.display = "block";
          node = node.parentElement;
        }
      },
      hideShow: function (forms) {
        forms.hide.forEach((form) => {
          document.getElementById(form + "-container").style.display = "none";
        });
        forms.show.forEach((form) => {
          let node = document.getElementById(form + "-container");
          while (node.tagName != "BODY") {
            node.style.display = "block";
            node = node.parentElement;
          }
        });
      },
    };
  }

  // #endregion add-ons loading //

  // #region add-ons/modules handling //
  function moduleHandle_sankeychart() {
    init();

    function init() {
      moduleInfo.sankeychart.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_forcechart() {
    init();

    function init() {
      moduleInfo.forcechart.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_chart1() {
    init();

    function init() {
      moduleInfo.chart1.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_chart3() {
    init();

    function init() {
      moduleInfo.chart3.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_chart4() {
    init();

    function init() {
      moduleInfo.chart4.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_chart5() {
    init();

    function init() {
      moduleInfo.chart5.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  function moduleHandle_chart6() {
    init();

    function init() {
      moduleInfo.chart6.method.init(moduleData);
    }

    return {
      init: function () {
        init();
      },
      event: function (arg) {},
    };
  }
  // #endregion add-ons/modules handling //
}
