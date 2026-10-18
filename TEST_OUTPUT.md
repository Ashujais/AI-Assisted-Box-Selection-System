# Test Run Output

**Generated At:** 2026-10-18 17:36:35
**Python Version:** Python 3.12.10
**Django Version:** Django 6.1
**Pytest Version:** pytest 8.4.1 / pytest-django 4.14.0

---

## 1. Django Test Runner (`python manage.py test --verbosity=2`)

```text
Found 32 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, boxes, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying boxes.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).

Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

test_get_boxes_list (boxes.tests.test_api.BoxAPITestCase.test_get_boxes_list) ... ok
test_get_products_list (boxes.tests.test_api.BoxAPITestCase.test_get_products_list) ... ok
test_order_recommend_action (boxes.tests.test_api.BoxAPITestCase.test_order_recommend_action) ... ok
test_order_select_box_action (boxes.tests.test_api.BoxAPITestCase.test_order_select_box_action) ... ok
test_recommend_box_api_adhoc_items (boxes.tests.test_api.BoxAPITestCase.test_recommend_box_api_adhoc_items) ... ok
test_recommend_box_api_by_order_id (boxes.tests.test_api.BoxAPITestCase.test_recommend_box_api_by_order_id) ... ok
test_recommend_box_api_invalid_payload (boxes.tests.test_api.BoxAPITestCase.test_recommend_box_api_invalid_payload) ... ok
test_box_properties (boxes.tests.test_models.ModelTestCase.test_box_properties) ... ok
test_order_item_properties (boxes.tests.test_models.ModelTestCase.test_order_item_properties) ... ok
test_order_properties (boxes.tests.test_models.ModelTestCase.test_order_properties) ... ok
test_packing_log_creation (boxes.tests.test_models.ModelTestCase.test_packing_log_creation) ... ok
test_product_properties (boxes.tests.test_models.ModelTestCase.test_product_properties) ... ok
test_recommend_for_custom_items (boxes.tests.test_recommendation_service.RecommendationServiceTestCase.test_recommend_for_custom_items) ... ok
test_recommend_for_order_persists_log_and_box (boxes.tests.test_recommendation_service.RecommendationServiceTestCase.test_recommend_for_order_persists_log_and_box) ... ok
test_box_list_view (boxes.tests.test_views.WebViewsTestCase.test_box_list_view) ... ok
test_dashboard_view (boxes.tests.test_views.WebViewsTestCase.test_dashboard_view) ... ok
test_interactive_recommender_view (boxes.tests.test_views.WebViewsTestCase.test_interactive_recommender_view) ... ok
test_order_detail_view_get (boxes.tests.test_views.WebViewsTestCase.test_order_detail_view_get) ... ok
test_order_detail_view_post_run_recommendation (boxes.tests.test_views.WebViewsTestCase.test_order_detail_view_post_run_recommendation) ... ok
test_order_detail_view_post_select_box (boxes.tests.test_views.WebViewsTestCase.test_order_detail_view_post_select_box) ... ok
test_order_list_view (boxes.tests.test_views.WebViewsTestCase.test_order_list_view) ... ok
test_product_list_view (boxes.tests.test_views.WebViewsTestCase.test_product_list_view) ... ok
test_3d_overlap_detection (boxes.tests.test_packing_service.PackingServiceTestCase.test_3d_overlap_detection) ... ok
test_cost_minimization_recommendation (boxes.tests.test_packing_service.PackingServiceTestCase.test_cost_minimization_recommendation) ... ok
test_dimensional_boundary_rejection (boxes.tests.test_packing_service.PackingServiceTestCase.test_dimensional_boundary_rejection) ... ok
test_empty_items_returns_no_fit (boxes.tests.test_packing_service.PackingServiceTestCase.test_empty_items_returns_no_fit) ... ok
test_multi_box_plan_generation (boxes.tests.test_packing_service.PackingServiceTestCase.test_multi_box_plan_generation) ... ok
test_rotations_generation (boxes.tests.test_packing_service.PackingServiceTestCase.test_rotations_generation) ... ok
test_single_item_rotation_fit (boxes.tests.test_packing_service.PackingServiceTestCase.test_single_item_rotation_fit) ... ok
test_tie_breaking_by_smaller_volume (boxes.tests.test_packing_service.PackingServiceTestCase.test_tie_breaking_by_smaller_volume) ... ok
test_volume_capacity_rejection (boxes.tests.test_packing_service.PackingServiceTestCase.test_volume_capacity_rejection) ... ok
test_weight_capacity_rejection (boxes.tests.test_packing_service.PackingServiceTestCase.test_weight_capacity_rejection) ... ok

----------------------------------------------------------------------
Ran 32 tests in 0.379s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

---

## 2. Pytest Runner (`pytest -v`)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.4.1, pluggy-1.6.0 -- C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
django: version: 6.1, settings: config.settings (from ini)
rootdir: F:\Tradexa_Django
configfile: pytest.ini
plugins: anyio-4.14.2, langsmith-0.10.18, django-4.14.0
collecting ... collected 32 items

boxes/tests/test_api.py::BoxAPITestCase::test_get_boxes_list PASSED      [  3%]
boxes/tests/test_api.py::BoxAPITestCase::test_get_products_list PASSED   [  6%]
boxes/tests/test_api.py::BoxAPITestCase::test_order_recommend_action PASSED [  9%]
boxes/tests/test_api.py::BoxAPITestCase::test_order_select_box_action PASSED [ 12%]
boxes/tests/test_api.py::BoxAPITestCase::test_recommend_box_api_adhoc_items PASSED [ 15%]
boxes/tests/test_api.py::BoxAPITestCase::test_recommend_box_api_by_order_id PASSED [ 18%]
boxes/tests/test_api.py::BoxAPITestCase::test_recommend_box_api_invalid_payload PASSED [ 21%]
boxes/tests/test_models.py::ModelTestCase::test_box_properties PASSED    [ 25%]
boxes/tests/test_models.py::ModelTestCase::test_order_item_properties PASSED [ 28%]
boxes/tests/test_models.py::ModelTestCase::test_order_properties PASSED  [ 31%]
boxes/tests/test_models.py::ModelTestCase::test_packing_log_creation PASSED [ 34%]
boxes/tests/test_models.py::ModelTestCase::test_product_properties PASSED [ 37%]
boxes/tests/test_recommendation_service.py::RecommendationServiceTestCase::test_recommend_for_custom_items PASSED [ 40%]
boxes/tests/test_recommendation_service.py::RecommendationServiceTestCase::test_recommend_for_order_persists_log_and_box PASSED [ 43%]
boxes/tests/test_views.py::WebViewsTestCase::test_box_list_view PASSED   [ 46%]
boxes/tests/test_views.py::WebViewsTestCase::test_dashboard_view PASSED  [ 50%]
boxes/tests/test_views.py::WebViewsTestCase::test_interactive_recommender_view PASSED [ 53%]
boxes/tests/test_views.py::WebViewsTestCase::test_order_detail_view_get PASSED [ 56%]
boxes/tests/test_views.py::WebViewsTestCase::test_order_detail_view_post_run_recommendation PASSED [ 59%]
boxes/tests/test_views.py::WebViewsTestCase::test_order_detail_view_post_select_box PASSED [ 62%]
boxes/tests/test_views.py::WebViewsTestCase::test_order_list_view PASSED [ 65%]
boxes/tests/test_views.py::WebViewsTestCase::test_product_list_view PASSED [ 68%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_3d_overlap_detection PASSED [ 71%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_cost_minimization_recommendation PASSED [ 75%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_dimensional_boundary_rejection PASSED [ 78%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_empty_items_returns_no_fit PASSED [ 81%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_multi_box_plan_generation PASSED [ 84%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_rotations_generation PASSED [ 87%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_single_item_rotation_fit PASSED [ 90%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_tie_breaking_by_smaller_volume PASSED [ 93%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_volume_capacity_rejection PASSED [ 96%]
boxes/tests/test_packing_service.py::PackingServiceTestCase::test_weight_capacity_rejection PASSED [100%]

============================= 32 passed in 2.19s ==============================
```

---

## Summary

- **Total Test Cases Executed:** 32 tests
- **Failed Tests:** 0
- **Errors:** 0
- **Status:** **ALL TESTS PASSED (100% Success Rate)**
- **Coverage Areas:**
  - Data Models (`Product`, `Box`, `Order`, `OrderItem`, `PackingLog`)
  - 3D Packing Simulation (6-DOF Rotations, 3D Collision Detection, Boundary Checks)
  - Box Selection Heuristics (Cost Minimization, Volume Tie-Breaking, Utilization)
  - Diagnostic Feedback on Rejection (Weight, Volume, Dimensional Bounds)
  - Multi-Box Shipment Fallback
  - High-level ORM Recommendation Orchestration
  - REST API Endpoints (`/api/recommend/`, ViewSets)
  - Warehouse UI Views (Dashboard, Order Detail, Recommender, Catalogs)
