import {
  ButtonItem,
  definePlugin,
  DialogButton,
  Menu,
  MenuItem,
  PanelSection,
  PanelSectionRow,
  Router,
  ServerAPI,
  showContextMenu,
  staticClasses,
  SteamClient,
  LifetimeNotification
} from "decky-frontend-lib";
import { VFC } from "react";
import { FaShip } from "react-icons/fa";
import SteamID from "steamid";

import logo from "../assets/logo.png";

declare let App: any

const Content: VFC<{ serverAPI: ServerAPI }> = ({}) => {
  // const [result, setResult] = useState<number | undefined>();

  // const onClick = async () => {
  //   const result = await serverAPI.callPluginMethod<AddMethodArgs, number>(
  //     "add",
  //     {
  //       left: 2,
  //       right: 2,
  //     }
  //   );
  //   if (result.success) {
  //     setResult(result.result);
  //   }
  // };
  
  return (
    <PanelSection title="Panel Section">
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={(e) =>
            showContextMenu(
              <Menu label="Menu" cancelText="CAAAANCEL" onCancel={() => {}}>
                <MenuItem onSelected={() => {}}>Item #1</MenuItem>
                <MenuItem onSelected={() => {}}>Item #2</MenuItem>
                <MenuItem onSelected={() => {}}>Item #3</MenuItem>
              </Menu>,
              e.currentTarget ?? window
            )
          }
        >
          Server says yolo
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src={logo} />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Router.CloseSideMenus();
            Router.Navigate("/deckshot");
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckshotPluginRouter: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Router.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  serverApi.routerHook.addRoute("/deckshot", DeckshotPluginRouter, {
    exact: true,
  });

  /*
  const startHook = SteamClient.Apps.RegisterForGameActionStart((actionType: number, id: string, action: string) => {
    console.log("Deckshot GameActionStart", actionType, id, action);
    
    Deckshot GameActionStart 1 648800 LaunchApp - when lanched raft

    serverAPI.callPluginMethod<GameActionStartParams, {}>("on_game_start_callback", {
      idk: actionType,
      game_id: id,
      action: action
    }).then(() => updatePlaytimesThrottled(serverAPI)); 
});
  */

  
  // RegisterForGameActionTaskChange doesn't seem useful - similar to GameActionStart
  // RegisterForGameActionUserRequest doesn't seem useful - similar to GameActionStart
  // RegisterForAppOverviewChanges returns nasty binary arrays
  // RegisterForAppDetails not useful
  // RegisterForGameActionShowUI not useful
  // RegisterForGameActionShowError not useful
  // RegisterForWorkshopChanges not useful
  // YAY! Deckshot RegisterForAppLifetimeNotifications {unAppID: 648800, nInstanceID: 28768, bRunning: true} is a
  // LifetimeNotification
  const taskHook = SteamClient.GameSessions.RegisterForAppLifetimeNotifications((n: LifetimeNotification) => {
    console.log("Deckshot AppLifetimeNotification", n);

    if (!n.bRunning) {
      serverApi.callPluginMethod("do_backup", {
        game_id: n.unAppID
      }).then((r) =>
        console.log("Python replied", r.result))
    }
  });


  let sid = new SteamID(App.m_CurrentUser.strSteamID); 

  serverApi.callPluginMethod("set_account_id", {
    id_num: sid.accountid
  }).then((r) =>
    console.log("Python replied", r.result))

  return {
    title: <div className={staticClasses.Title}>Deckshot</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      taskHook!.unregister();
      serverApi.routerHook.removeRoute("/deckshot");
    },
  };
});
