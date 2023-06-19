var modules = {};
async function load() {
  return await fetch(
    window.location.origin + "/static/assets/html/modules.html"
  )
    .then(function (e) {
      return e.text();
    })
    .then(function (e) {
      return new DOMParser().parseFromString(e, "text/html");
    })
    .catch(function (e) {});
}
async function load1() {
  let e = await fetch(
      window.location.origin + "/static/assets/html/modules.html"
    ),
    t = await e.text();
  return new DOMParser().parseFromString(t, "text/html");
}
async function caller() {
  (modules.addons = await load1()), startModule();
}
caller();
var moduleInfo = {},
  moduleData = {};
function startModule() {
  function preprocessData() {
    (moduleData.nodes = JSON.parse(
      document.getElementById("nodes").value.replaceAll("'", '"')
    ).sort((e, t) => o(e, t, "id"))),
      (moduleData.links = JSON.parse(
        document.getElementById("links").value.replaceAll("'", '"')
      )),
      (moduleData.source = JSON.parse(
        document
          .getElementById("data_of_source_chain")
          .value.replaceAll("'", '"')
      ).sort((e, t) => o(e, t, "date"))),
      (moduleData.destination = JSON.parse(
        document
          .getElementById("data_of_destination_chain")
          .value.replaceAll("'", '"')
      ).sort((e, t) => o(e, t, "date")));
    let e = "";
    moduleData.nodeList = {};
    const t = new Array(moduleData.nodes.length).fill(0);
    for (i = 0; i < moduleData.nodes.length; i++)
      moduleData.nodeList[moduleData.nodes[i].id] = i;
    function o(e, t, o) {
      return e[o] < t[o] ? -1 : e[o] > t[o] ? 1 : 0;
    }
    (moduleData.sourceStacked = []),
      (moduleData.sourceStacked100 = []),
      moduleData.source.forEach((o) => {
        o.date != e
          ? ((e = o.date),
            moduleData.sourceStacked.push([o.date, ...t]),
            (moduleData.sourceStacked[moduleData.sourceStacked.length - 1][
              moduleData.nodeList[o.sourcechain] + 1
            ] = o.value))
          : (moduleData.sourceStacked[moduleData.sourceStacked.length - 1][
              moduleData.nodeList[o.sourcechain] + 1
            ] = o.value);
      }),
      (moduleData.sourceStacked100 = moduleData.sourceStacked.map((e) => {
        const [t, ...o] = e;
        return [o.reduce((e, t) => e + t), t, ...o];
      })),
      (moduleData.sourceStacked100 = moduleData.sourceStacked100.map((e) => {
        const [t, o, ...a] = e,
          n = a.map((e) => e / t || 0);
        return [t, o, ...n];
      })),
      moduleData.sourceStacked100.forEach((e) => e.splice(0, 1)),
      (moduleData.destinationStacked = []),
      (moduleData.destinationStacked100 = []),
      (e = ""),
      moduleData.destination.forEach((o) => {
        o.date != e
          ? ((e = o.date),
            moduleData.destinationStacked.push([o.date, ...t]),
            (moduleData.destinationStacked[
              moduleData.destinationStacked.length - 1
            ][moduleData.nodeList[o.destinationchain] + 1] = o.value))
          : (moduleData.destinationStacked[
              moduleData.destinationStacked.length - 1
            ][moduleData.nodeList[o.destinationchain] + 1] = o.value);
      }),
      (moduleData.destinationStacked100 = moduleData.destinationStacked.map(
        (e) => {
          const [t, ...o] = e;
          return [o.reduce((e, t) => e + t), t, ...o];
        }
      )),
      (moduleData.destinationStacked100 = moduleData.destinationStacked100.map(
        (e) => {
          const [t, o, ...a] = e,
            n = a.map((e) => e / t || 0);
          return [t, o, ...n];
        }
      )),
      moduleData.destinationStacked100.forEach((e) => e.splice(0, 1)),
      (moduleData.color = [
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
      ]),
      (moduleData.vars = {
        svgurl: window.location.origin + "/static/images/",
        forcechart: { title: "Asset Flow Network" },
        sankychart: { title: "Flow Diagarm" },
        chart1: { title: "Total Volume Of Bridge" },
        chart3: { title: "Daily Volume Of Bridge by Source - axlUSDC" },
        chart4: { title: "Daily Volume Of Bridge by Target - axlUSDC" },
        chart5: { title: "Normalized Daily Volume Of Bridge by Source" },
        chart6: { title: "Normalized Daily Volume Of Bridge by Target" },
      });
  }
  function moduleManage() {
    const load = (module) => {
        module = { ...module, script: "", method: {}, event: {} };
        let src = modules[module.core].getElementById(
            module.name + "-container"
          ),
          des = document.getElementById(module.name + "-container");
        return (
          (des.innerHTML = src.innerHTML),
          null != des.querySelector("script") &&
            eval(
              "module.script = " + des.querySelector("script").innerHTML.trim()
            ),
          module
        );
      },
      loadModule = (module) => {
        null == moduleInfo[module.name]
          ? ((module = load(module)),
            (module.init = eval("moduleHandle_" + module.name)),
            (module.method = module.script()),
            (moduleInfo[module.name] = {
              core: module.core,
              name: module.name,
              script: module.script,
              method: module.method.method,
              init: module.init,
            }),
            (module.ret = module.init()),
            moduleInfo[module.name].method.setCallback(module.ret.event),
            (moduleInfo[module.name].event = module.ret.event))
          : ((module = moduleInfo[module.name]), (module.ret = module.init()));
      },
      unloadModule = (e) => {
        (document.getElementById(e + "-container").innerHTML = ""),
          delete moduleInfo[e];
      };
    return {
      loadModules: function (e) {
        e.forEach((e) => loadModule(e));
      },
      loadModule: loadModule,
      unloadModuleAll: function () {
        Object.keys(moduleInfo).forEach((e) => unloadModule(e));
      },
      unloadModule: unloadModule,
    };
  }
  function visibility() {
    return {
      hideForm: function (e) {
        document.getElementById(e + "-container").style.display = "none";
      },
      showForm: function (e) {
        let t = document.getElementById(e + "-container");
        for (; "BODY" != t.tagName; )
          (t.style.display = "block"), (t = t.parentElement);
      },
      hideShow: function (e) {
        e.hide.forEach((e) => {
          document.getElementById(e + "-container").style.display = "none";
        }),
          e.show.forEach((e) => {
            let t = document.getElementById(e + "-container");
            for (; "BODY" != t.tagName; )
              (t.style.display = "block"), (t = t.parentElement);
          });
      },
    };
  }
  function moduleHandle_sankeychart() {
    function e() {
      moduleInfo.sankeychart.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_forcechart() {
    function e() {
      moduleInfo.forcechart.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_chart1() {
    function e() {
      moduleInfo.chart1.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_chart3() {
    function e() {
      moduleInfo.chart3.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_chart4() {
    function e() {
      moduleInfo.chart4.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_chart5() {
    function e() {
      moduleInfo.chart5.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  function moduleHandle_chart6() {
    function e() {
      moduleInfo.chart6.method.init(moduleData);
    }
    return (
      e(),
      {
        init: function () {
          e();
        },
        event: function (e) {},
      }
    );
  }
  preprocessData(),
    moduleManage().loadModules([
      { core: "addons", name: "sankeychart" },
      { core: "addons", name: "forcechart" },
      { core: "addons", name: "chart1" },
      { core: "addons", name: "chart3" },
      { core: "addons", name: "chart4" },
      { core: "addons", name: "chart5" },
      { core: "addons", name: "chart6" },
    ]);
}
