from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('config.urls'))
]

import debug_toolbar

urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
]