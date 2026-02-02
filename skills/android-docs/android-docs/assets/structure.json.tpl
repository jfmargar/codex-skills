{
  "project": {
    "name": "{{project_name}}",
    "type": "Android",
    "modules": {{modules_json}},
    "entryPoints": {
      "application": "{{entry_application}}",
      "launcher": "{{entry_launcher}}",
      "login": "{{entry_login}}"
    }
  },
  "app": {
    "description": "{{app_description}}",
    "paths": {
      "router": "{{app_router}}",
      "apiModule": "{{app_api_module}}",
      "apiServices": "{{app_api_services}}",
      "domain": "{{app_domain}}",
      "ui": "{{app_ui}}",
      "assetsPdf": "{{app_assets}}"
    }
  },
  "dabase": {
    "description": "{{dabase_description}}",
    "paths": {
      "presentInjector": "{{dabase_present_injector}}",
      "contextModule": "{{dabase_context_module}}",
      "routerModule": "{{dabase_router_module}}",
      "securedApiModule": "{{dabase_secured_module}}",
      "unsecuredApiModule": "{{dabase_unsecured_module}}",
      "basePresenter": "{{dabase_base_presenter}}",
      "navigate": "{{dabase_navigate}}"
    }
  }
}
