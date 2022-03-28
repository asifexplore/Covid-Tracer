# ADMIN
ADMIN_TABLE_NAME = 'admins'
ADMIN_ALL_COLUMNS = ('id', 'username', 'password', 'created_at', 'updated_at')
ADMIN_EDITABALE_COLUMNS = ('username', 'password')
# ADMIN END

# CITIZEN
CITIZEN_TABLE_NAME = 'citizens'
CITIZEN_ALL_COLUMNS = ('id', 'full_name', 'nric', 'address', 'mobile',
                       'date_of_birth', 'gender', 'created_at', 'updated_at')
CITIZEN_EDITABALE_COLUMNS = ('full_name', 'nric', 'address', 'mobile',
                             'date_of_birth', 'gender')
# CITIZEN END

# VACCINE
VACCINE_TABLE_NAME = 'vaccines'
VACCINE_ALL_COLUMNS = ('id', 'name', 'type', 'created_at', 'updated_at')
VACCINE_EDITABALE_COLUMNS = ('name', 'type')
# VACCINE END

# AREA
AREA_TABLE_NAME = 'areas'
AREA_ALL_COLUMNS = ('id', 'name', 'region', 'created_at', 'updated_at')
AREA_EDITABALE_COLUMNS = ('name', 'region')
# AREA END

# LANDMARK
LANDMARK_TABLE_NAME = 'landmarks'
LANDMARK_ALL_COLUMNS = ('id', 'area_id', 'name',
                        'latitude', 'longitude',
                        'created_at', 'updated_at')
LANDMARK_EDITABALE_COLUMNS = ('area_id', 'name',
                              'latitude', 'longitude')
# LANDMARK END

# HEALTH HISTORY
HEALTH_HISTORY_TABLE_NAME = 'health_historys'
HEALTH_HISTORY_ALL_COLUMNS = ('id', 'citizen_id', 'updated_by_id',
                              'status', 'created_at', 'updated_at')
HEALTH_HISTORY_EDITABALE_COLUMNS = ()
# HEALTH HISTORY END

# VACCINATION HISTORY
VACCINATION_HISTORY_TABLE_NAME = 'vaccination_historys'
VACCINATION_HISTORY_ALL_COLUMNS = ('id', 'citizen_id', 'updated_by_id',
                                   'vaccine_id', 'dose_type',
                                   'created_at', 'updated_at')
VACCINATION_HISTORY_EDITABALE_COLUMNS = ()
# VACCINATION HISTORY END

# CITIZEN LANDMARK FOOTPRINT
CITIZEN_LANDMARK_FOOTPRINT_TABLE_NAME = 'citizen_landmark_footprints'
CITIZEN_LANDMARK_FOOTPRINT_ALL_COLUMNS = ('id', 'citizen_id', 'landmark_id',
                                          'created_at', 'updated_at')
CITIZEN_LANDMARK_FOOTPRINT_EDITABALE_COLUMNS = ()
# CITIZEN LANDMARK FOOTPRINT END

# CITIZEN IN CLUSTER
CITIZENS_IN_CLUSTER_TABLE_NAME = 'citizens_in_clusters'
CITIZENS_IN_CLUSTER_ALL_COLUMNS = ('id', 'cluster_id', 'citizen_id')
CITIZENS_IN_CLUSTER_EDITABALE_COLUMNS = ()
# CITIZEN IN CLUSTER END

# CLUSTER
CLUSTER_TABLE_NAME = 'clusters'
CLUSTER_ALL_COLUMNS = ('id', 'landmark_id', 'status',
                       'created_at', 'updated_at')
CLUSTER_EDITABALE_COLUMNS = ()
# CLUSTER END

NUM_ROW_PER_PAGE = 8

DAY_UNIT = 'day'
WEEK_UNIT = 'week'
MONTH_UNIT = 'month'
YEAR_UNIT = 'year'
ALL_UNIT = 'all'

HOUR_IN_DAY = 24
DAY_IN_DAY = 1
DAY_IN_WEEK = 7
DAY_IN_MONTH = 30
DAY_IN_YEAR = 365

SECOND_IN_YEAR = 31536000
SECOND_IN_MONTH = 2629800
SECOND_IN_WEEK = 604800
SECOND_IN_DAY = 86400

OLDEST = 'oldest'
YOUNGEST = 'youngest'

VACCINATED = 'vaccinated'
INFECTED = 'infected'
